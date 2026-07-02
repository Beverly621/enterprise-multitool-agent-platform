from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_run import AgentTrace
from app.models.audit_log import AuditLog
from app.models.tool import AgentTool, Approval, EmailDraft, ToolCall
from app.models.user import User
from app.services.tool_permission_service import require_tool_access
from app.services.tool_registry import ToolRegistry, normalize_tool_name
from app.services.tool_validation_service import ToolValidationError, validate_tool_args
from app.tools import ToolContext

SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization"}


async def invoke_tool(
    db: Session,
    user: User,
    tool_name: str,
    args: dict[str, Any],
    run_id: str | None = None,
    step_id: int | None = None,
    session_id: str | None = None,
) -> ToolCall:
    registry = ToolRegistry(db)
    registry.sync_builtin_tools()
    normalized_name = normalize_tool_name(tool_name)
    tool_record = registry.get_tool_record(normalized_name)
    if tool_record is None:
        tool_call = ToolCall(
            tool_call_id=f"tc_{uuid.uuid4().hex}",
            run_id=run_id,
            step_id=step_id,
            user_id=user.id,
            tool_name=normalized_name,
            tool_args=_sanitize_args(args),
            status="PENDING",
            requires_approval=False,
        )
        db.add(tool_call)
        db.flush()
        _mark_failed(db, tool_call, "Tool not found")
        _audit(
            db,
            user.id,
            "TOOL_FAILED",
            "tool_call",
            tool_call.tool_call_id,
            {"tool_name": normalized_name, "error": "Tool not found"},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    tool_call = ToolCall(
        tool_call_id=f"tc_{uuid.uuid4().hex}",
        run_id=run_id,
        step_id=step_id,
        user_id=user.id,
        tool_name=normalized_name,
        tool_args=_sanitize_args(args),
        status="PENDING",
        requires_approval=tool_record.require_approval or tool_record.requires_approval,
    )
    db.add(tool_call)
    db.flush()

    try:
        _trace(db, tool_call, "TOOL_CALL_STARTED", {"tool_name": normalized_name})
        if not tool_record.enabled or not tool_record.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tool is disabled")

        require_tool_access(user, tool_record)
        _trace(
            db,
            tool_call,
            "TOOL_PERMISSION_CHECKED",
            {"permission": tool_record.permission_level},
        )

        validate_tool_args(tool_record.schema_json, args)
        _trace(db, tool_call, "TOOL_ARGS_VALIDATED", {"schema": tool_record.schema_json})

        builtin_tool = registry.get_builtin(normalized_name)
        if builtin_tool is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only built-in whitelisted tools are executable in this phase.",
            )

        if tool_record.require_approval or tool_record.requires_approval:
            approval = _create_approval(db, tool_call, tool_record, user, args)
            tool_call.status = "WAITING_APPROVAL"
            tool_call.approval_id = approval.id
            tool_call.tool_result = {
                "approval_id": approval.approval_id,
                "status": "WAITING_APPROVAL",
                **(approval.request_payload or {}),
            }
            _trace(db, tool_call, "TOOL_WAITING_APPROVAL", {"approval_id": approval.approval_id})
            _audit(
                db,
                user.id,
                "TOOL_APPROVAL_CREATED",
                "approval",
                approval.approval_id,
                {"tool_call_id": tool_call.tool_call_id, "tool_name": normalized_name},
            )
            db.commit()
            db.refresh(tool_call)
            return tool_call

        context = ToolContext(
            db=db,
            user=user,
            run_id=run_id,
            step_id=step_id,
            session_id=session_id,
        )
        await _execute_with_retry(tool_call, builtin_tool, args, context, tool_record)
        db.commit()
        db.refresh(tool_call)
        return tool_call
    except HTTPException as exc:
        _mark_failed(db, tool_call, str(exc.detail))
        _audit(
            db,
            user.id,
            "TOOL_FAILED",
            "tool_call",
            tool_call.tool_call_id,
            {"tool_name": normalized_name, "error": str(exc.detail)},
        )
        db.commit()
        raise
    except ToolValidationError as exc:
        _mark_failed(db, tool_call, str(exc))
        _audit(
            db,
            user.id,
            "TOOL_FAILED",
            "tool_call",
            tool_call.tool_call_id,
            {"tool_name": normalized_name, "error": str(exc)},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        _mark_failed(db, tool_call, str(exc))
        _audit(
            db,
            user.id,
            "TOOL_FAILED",
            "tool_call",
            tool_call.tool_call_id,
            {"tool_name": normalized_name, "error": str(exc)},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


def get_tool_call(db: Session, tool_call_id: str, user: User) -> ToolCall:
    tool_call = db.scalar(select(ToolCall).where(ToolCall.tool_call_id == tool_call_id))
    if tool_call is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool call not found")
    if tool_call.user_id != user.id and not any(role.name == "Admin" for role in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to tool call")
    return tool_call


def list_run_tool_calls(db: Session, run_id: str, user: User) -> list[ToolCall]:
    statement = select(ToolCall).where(ToolCall.run_id == run_id).order_by(ToolCall.id)
    if not any(role.name == "Admin" for role in user.roles):
        statement = statement.where(ToolCall.user_id == user.id)
    return list(db.scalars(statement).all())


def serialize_tool_call(tool_call: ToolCall) -> dict[str, Any]:
    return {
        "id": tool_call.id,
        "tool_call_id": tool_call.tool_call_id,
        "run_id": tool_call.run_id,
        "user_id": tool_call.user_id,
        "tool_name": tool_call.tool_name,
        "tool_args": tool_call.tool_args,
        "tool_result": tool_call.tool_result,
        "status": tool_call.status,
        "duration_ms": tool_call.duration_ms,
        "requires_approval": tool_call.requires_approval,
        "approval_id": tool_call.approval_id,
        "error_message": tool_call.error_message,
        "created_at": tool_call.created_at,
        "updated_at": tool_call.updated_at,
    }


async def _execute_with_retry(
    tool_call: ToolCall,
    tool: Any,
    args: dict[str, Any],
    context: ToolContext,
    tool_record: AgentTool,
) -> None:
    attempts = max(tool_record.retry_count, 0) + 1
    started = time.perf_counter()
    last_error: str | None = None
    for attempt in range(1, attempts + 1):
        try:
            tool_call.status = "RUNNING"
            result = await asyncio.wait_for(
                tool.execute(args, context),
                timeout=tool_record.timeout_ms / 1000,
            )
            tool_call.status = "SUCCESS"
            tool_call.tool_result = _summarize_result(result)
            tool_call.duration_ms = int((time.perf_counter() - started) * 1000)
            tool_call.updated_at = datetime.now(UTC)
            _trace(context.db, tool_call, "TOOL_CALL_SUCCESS", {"attempt": attempt})
            _audit(
                context.db,
                context.user.id,
                "TOOL_INVOKED",
                "tool_call",
                tool_call.tool_call_id,
                {"tool_name": tool_call.tool_name, "status": "SUCCESS"},
            )
            return
        except TimeoutError:
            last_error = "Tool execution timed out"
            tool_call.status = "TIMEOUT"
            _trace(context.db, tool_call, "TOOL_CALL_TIMEOUT", {"attempt": attempt})
        except Exception as exc:
            last_error = str(exc)
            _trace(
                context.db,
                tool_call,
                "TOOL_CALL_RETRY",
                {"attempt": attempt, "error": last_error},
            )
        if attempt < attempts:
            await asyncio.sleep(0)
    tool_call.status = "FAILED"
    tool_call.error_message = last_error or "Tool execution failed"
    tool_call.duration_ms = int((time.perf_counter() - started) * 1000)
    tool_call.updated_at = datetime.now(UTC)
    _trace(context.db, tool_call, "TOOL_CALL_FAILED", {"error": tool_call.error_message})
    raise RuntimeError(tool_call.error_message)


def _create_approval(
    db: Session,
    tool_call: ToolCall,
    tool_record: AgentTool,
    user: User,
    args: dict[str, Any],
) -> Approval:
    request_payload = _sanitize_args(args)
    if tool_record.name == "send_email_draft":
        draft = EmailDraft(
            draft_id=f"draft_{uuid.uuid4().hex}",
            user_id=user.id,
            to_email=args["to_email"],
            subject=args["subject"],
            body=args["body"],
            source_run_id=tool_call.run_id,
        )
        db.add(draft)
        db.flush()
        request_payload = {**request_payload, "draft_id": draft.draft_id}

    approval = Approval(
        approval_id=f"ap_{uuid.uuid4().hex}",
        tool_call_id=tool_call.tool_call_id,
        user_id=user.id,
        tool_name=tool_record.name,
        approval_type="TOOL_CALL",
        requester_id=user.id,
        requested_by=user.id,
        run_id=tool_call.run_id,
        status="PENDING",
        payload_json=request_payload,
        request_payload=request_payload,
    )
    db.add(approval)
    db.flush()
    return approval


def _mark_failed(db: Session, tool_call: ToolCall, error_message: str) -> None:
    tool_call.status = "FAILED"
    tool_call.error_message = error_message
    tool_call.updated_at = datetime.now(UTC)
    _trace(db, tool_call, "TOOL_CALL_FAILED", {"error": error_message})


def _trace(db: Session, tool_call: ToolCall, event_name: str, metadata: dict[str, Any]) -> None:
    db.add(
        AgentTrace(
            run_id=tool_call.run_id or tool_call.tool_call_id,
            event_type="tool",
            event_name=event_name,
            content=tool_call.tool_name,
            metadata_json={
                "tool_call_id": tool_call.tool_call_id,
                "tool_name": tool_call.tool_name,
                **metadata,
            },
        )
    )


def _audit(
    db: Session,
    actor_id: int | None,
    action: str,
    resource_type: str,
    resource_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata,
        )
    )


def _sanitize_args(args: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in args.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "***"
        elif isinstance(value, str) and len(value) > 1000:
            sanitized[key] = value[:1000] + "...[truncated]"
        else:
            sanitized[key] = value
    return sanitized


def _summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    summary = dict(result)
    if "rows" in summary and isinstance(summary["rows"], list) and len(summary["rows"]) > 20:
        summary["rows"] = summary["rows"][:20]
        summary["truncated"] = True
    if (
        "content" in summary
        and isinstance(summary["content"], str)
        and len(summary["content"]) > 4000
    ):
        summary["content"] = summary["content"][:4000] + "...[truncated]"
    return summary
