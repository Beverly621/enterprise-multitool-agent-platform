from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.tool import Approval, EmailDraft, ToolCall
from app.models.user import User
from app.services.tool_permission_service import highest_role_level


def requires_human_approval(action: str) -> bool:
    return action in {"refund_request", "external_write", "sql_write", "send_email_draft"}


def list_approvals(db: Session, user: User) -> list[Approval]:
    statement = select(Approval).order_by(Approval.id.desc()).limit(100)
    if highest_role_level(user) < 3:
        statement = statement.where(Approval.requested_by == user.id)
    return list(db.scalars(statement).all())


def get_approval(db: Session, approval_id: str, user: User) -> Approval:
    approval = db.scalar(select(Approval).where(Approval.approval_id == approval_id))
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    if highest_role_level(user) < 3 and approval.requested_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to approval")
    return approval


def approve_request(
    db: Session,
    approval_id: str,
    approver: User,
    reason: str | None = None,
) -> Approval:
    approval = get_approval(db, approval_id, approver)
    _ensure_pending(approval)
    now = datetime.now(UTC)
    approval.status = "APPROVED"
    approval.reason = reason
    approval.approved_by = approver.id
    approval.approver_id = approver.id
    approval.approved_at = now
    approval.decided_at = now
    approval.updated_at = now
    approval.approval_result = {"approved": True, "reason": reason}
    _mark_related_records(db, approval, "APPROVED")
    _audit(db, approver.id, "TOOL_APPROVED", approval)
    db.commit()
    db.refresh(approval)
    return approval


def reject_request(
    db: Session,
    approval_id: str,
    approver: User,
    reason: str | None = None,
) -> Approval:
    approval = get_approval(db, approval_id, approver)
    _ensure_pending(approval)
    now = datetime.now(UTC)
    approval.status = "REJECTED"
    approval.reason = reason
    approval.approved_by = approver.id
    approval.approver_id = approver.id
    approval.rejected_at = now
    approval.decided_at = now
    approval.updated_at = now
    approval.approval_result = {"approved": False, "reason": reason}
    _mark_related_records(db, approval, "REJECTED")
    _audit(db, approver.id, "TOOL_REJECTED", approval)
    db.commit()
    db.refresh(approval)
    return approval


def serialize_approval(approval: Approval) -> dict:
    return {
        "id": approval.id,
        "approval_id": approval.approval_id,
        "tool_call_id": approval.tool_call_id,
        "user_id": approval.user_id,
        "tool_name": approval.tool_name,
        "approval_type": approval.approval_type,
        "status": approval.status,
        "reason": approval.reason,
        "request_payload": approval.request_payload or approval.payload_json,
        "approval_result": approval.approval_result,
        "requested_by": approval.requested_by or approval.requester_id,
        "approved_by": approval.approved_by or approval.approver_id,
        "created_at": approval.created_at,
        "updated_at": approval.updated_at,
        "approved_at": approval.approved_at,
        "rejected_at": approval.rejected_at,
    }


def _ensure_pending(approval: Approval) -> None:
    if approval.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval is already {approval.status}.",
        )


def _mark_related_records(db: Session, approval: Approval, status_value: str) -> None:
    payload = approval.request_payload or {}
    if draft_id := payload.get("draft_id"):
        draft = db.scalar(select(EmailDraft).where(EmailDraft.draft_id == draft_id))
        if draft is not None:
            draft.status = status_value
            draft.updated_at = datetime.now(UTC)

    if approval.tool_call_id:
        tool_call = db.scalar(
            select(ToolCall).where(ToolCall.tool_call_id == approval.tool_call_id)
        )
        if tool_call is not None:
            tool_call.status = "SUCCESS" if status_value == "APPROVED" else "REJECTED"
            tool_call.tool_result = {
                "approval_id": approval.approval_id,
                "approval_status": status_value,
                "draft_id": payload.get("draft_id"),
            }
            tool_call.updated_at = datetime.now(UTC)


def _audit(db: Session, actor_id: int | None, action: str, approval: Approval) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            resource_type="approval",
            resource_id=approval.approval_id,
            metadata_json={
                "tool_call_id": approval.tool_call_id,
                "tool_name": approval.tool_name,
                "status": approval.status,
            },
        )
    )
