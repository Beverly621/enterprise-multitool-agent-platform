from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.agent_run import AgentRun
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.report import Report
from app.models.task_progress import FailedTask, TaskProgress
from app.models.tool import Approval, ToolCall
from app.models.user import User
from app.services.tool_permission_service import highest_role_level

router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    user_id = None if highest_role_level(current_user) >= 3 else current_user.id
    return ok(
        {
            "knowledge_bases": _count(db, KnowledgeBase, user_id, "owner_id"),
            "documents": _count_documents(db, user_id),
            "agent_runs": _count(db, AgentRun, user_id, "user_id"),
            "tasks": _count(db, TaskProgress, user_id, "user_id"),
            "reports": _count(db, Report, user_id, "user_id"),
            "tool_calls": _count(db, ToolCall, user_id, "user_id"),
            "pending_approvals": _count_pending_approvals(db, user_id),
            "failed_tasks": _count(db, FailedTask, user_id, "user_id"),
            "recent_runs": _recent(db, AgentRun, user_id, "user_id"),
            "recent_reports": _recent(db, Report, user_id, "user_id"),
            "recent_tool_calls": _recent(db, ToolCall, user_id, "user_id"),
            "recent_audit_logs": _recent_audit_logs(db),
        }
    )


def _count(db: Session, model, user_id: int | None, user_field: str) -> int:
    statement = select(func.count()).select_from(model)
    if user_id is not None:
        statement = statement.where(getattr(model, user_field) == user_id)
    return int(db.scalar(statement) or 0)


def _count_documents(db: Session, user_id: int | None) -> int:
    statement = select(func.count()).select_from(Document)
    if user_id is not None:
        statement = statement.join(KnowledgeBase, KnowledgeBase.id == Document.kb_id).where(
            KnowledgeBase.owner_id == user_id
        )
    return int(db.scalar(statement) or 0)


def _count_pending_approvals(db: Session, user_id: int | None) -> int:
    statement = select(func.count()).select_from(Approval).where(Approval.status == "PENDING")
    if user_id is not None:
        statement = statement.where(Approval.user_id == user_id)
    return int(db.scalar(statement) or 0)


def _recent(db: Session, model, user_id: int | None, user_field: str) -> list[dict]:
    statement = select(model).order_by(model.id.desc()).limit(5)
    if user_id is not None:
        statement = statement.where(getattr(model, user_field) == user_id)
    return [_serialize_item(item) for item in db.scalars(statement).all()]


def _recent_audit_logs(db: Session) -> list[dict]:
    logs = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(5)).all()
    return [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "created_at": log.created_at,
        }
        for log in logs
    ]


def _serialize_item(item) -> dict:
    return {
        "id": getattr(item, "id", None),
        "run_id": getattr(item, "run_id", None),
        "task_id": getattr(item, "task_id", None),
        "report_id": getattr(item, "report_id", None),
        "tool_call_id": getattr(item, "tool_call_id", None),
        "title": getattr(item, "title", None),
        "query": getattr(item, "query", None),
        "intent": getattr(item, "intent", None),
        "status": getattr(item, "status", None),
        "created_at": getattr(item, "created_at", None),
        "updated_at": getattr(item, "updated_at", None),
    }
