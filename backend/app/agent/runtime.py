from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.nodes.approval_node import run_approval_node
from app.agent.nodes.final_node import run_final_node
from app.agent.nodes.general_chat_node import run_general_chat_node
from app.agent.nodes.intent_router import run_intent_router_node
from app.agent.nodes.rag_node import run_rag_node
from app.agent.nodes.report_node import run_report_node
from app.agent.nodes.sql_node import run_sql_node
from app.agent.nodes.tool_node import run_tool_node
from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.agent_step_service import add_step, add_trace
from app.services.tool_permission_service import highest_role_level


async def run_agent_chat(
    db: Session,
    user: User,
    query: str,
    session_id: str | None = None,
    kb_id: int | None = None,
) -> AgentState:
    run = _create_run(db, user, query, session_id)
    state: AgentState = {
        "run_id": run.run_id,
        "user_id": user.id,
        "session_id": session_id,
        "query": query,
        "kb_id": kb_id,
        "messages": [{"role": "user", "content": query}],
        "tool_results": [],
        "requires_approval": False,
        "approval_id": None,
        "current_step": "CREATED",
        "error": None,
        "metadata": {},
        "steps": [],
    }
    try:
        add_trace(db, run.run_id, "AGENT_RUN_CREATED", metadata_json={"user_id": user.id})
        db.add(
            AuditLog(
                actor_id=user.id,
                action="AGENT_RUN_CREATED",
                resource_type="agent_run",
                resource_id=run.run_id,
                metadata_json={"session_id": session_id},
            )
        )
        state = run_intent_router_node(db, run, state)
        run.intent = state["intent"]
        run.updated_at = datetime.now(UTC)
        db.flush()
        _enforce_planner_permission(user, state["intent"])

        if state["intent"] == "GENERAL_CHAT":
            state = run_general_chat_node(db, run, state)
        elif state["intent"] == "RAG_QA":
            state = run_rag_node(db, run, state, user)
        elif state["intent"] == "SQL_QUERY":
            state = run_sql_node(db, run, state, user)
        elif state["intent"] == "TOOL_CALL":
            state = await run_tool_node(db, run, state, user)
        elif state["intent"] == "MULTI_STEP_REPORT":
            state = run_sql_node(db, run, state, user, allow_user_report=True)
            if kb_id is not None:
                state = run_rag_node(db, run, state, user)
            else:
                add_step(
                    db,
                    run.run_id,
                    "RAG_RETRIEVAL",
                    "rag",
                    "SUCCESS",
                    input_json={"kb_id": None},
                    output_json={"skipped": True, "reason": "No kb_id provided."},
                )
            state = run_report_node(db, run, state, user)
        elif state["intent"] == "NEED_APPROVAL":
            state = await run_tool_node(db, run, state, user)
            state = run_approval_node(db, run, state)
        else:
            raise ValueError(f"Unsupported intent: {state['intent']}")

        state = run_final_node(db, run, state)
        db.commit()
        return state
    except Exception as exc:
        db.rollback()
        _mark_failed(db, run.run_id, str(exc), state)
        db.commit()
        state["error"] = str(exc)
        state["final_answer"] = _human_error(exc)
        state["current_step"] = "FAILED"
        return state


def _create_run(db: Session, user: User, query: str, session_id: str | None) -> AgentRun:
    run = AgentRun(
        run_id=f"run_{uuid.uuid4().hex}",
        user_id=user.id,
        session_id=session_id,
        query=query,
        intent="UNKNOWN",
        status="CREATED",
        current_step="CREATED",
    )
    db.add(run)
    db.flush()
    return run


def _enforce_planner_permission(user: User, intent: str) -> None:
    level = highest_role_level(user)
    if intent == "SQL_QUERY" and level < 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SQL_QUERY requires Developer role or higher.",
        )
    if intent in {"TOOL_CALL", "NEED_APPROVAL", "MULTI_STEP_REPORT"} and level < 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{intent} requires User role or higher.",
        )


def _mark_failed(db: Session, run_id: str, error: str, state: AgentState) -> None:
    run = db.scalar(select(AgentRun).where(AgentRun.run_id == run_id))
    if run is not None:
        run.status = "FAILED"
        run.current_step = state.get("current_step") or "FAILED"
        run.error_message = error
        run.finished_at = datetime.now(UTC)
        run.updated_at = datetime.now(UTC)
    else:
        run = AgentRun(
            run_id=run_id,
            user_id=state.get("user_id"),
            session_id=state.get("session_id"),
            query=state.get("query") or "",
            intent=state.get("intent"),
            status="FAILED",
            current_step=state.get("current_step") or "FAILED",
            error_message=error,
            finished_at=datetime.now(UTC),
        )
        db.add(run)
        db.flush()
    add_step(
        db,
        run_id,
        state.get("current_step") or "AGENT_RUNTIME",
        "agent",
        "FAILED",
        input_json={"intent": state.get("intent"), "query": state.get("query")},
        output_json={"error": error},
        error_message=error,
    )
    add_trace(
        db,
        run_id,
        "AGENT_RUN_FAILED",
        metadata_json={"error": error, "intent": state.get("intent")},
    )


def _human_error(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        return str(exc.detail)
    return "任务执行失败，已记录错误 Trace，请稍后重试或联系管理员。"


def response_from_state(state: AgentState) -> dict[str, Any]:
    return {
        "run_id": state.get("run_id"),
        "intent": state.get("intent"),
        "status": "FAILED" if state.get("error") else (
            "WAITING_APPROVAL" if state.get("requires_approval") else "SUCCESS"
        ),
        "answer": state.get("final_answer"),
        "approval_id": state.get("approval_id"),
        "trace_url": f"/api/runs/{state.get('run_id')}/traces",
        "citations": state.get("citations", []),
        "generated_sql": state.get("generated_sql"),
        "sql_result": state.get("sql_result"),
        "tool_results": state.get("tool_results", []),
        "error": state.get("error"),
    }
