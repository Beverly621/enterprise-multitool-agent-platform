from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import require_permissions
from app.models.audit_log import AuditLog
from app.models.user import User

router = APIRouter()


@router.get("")
def list_audit_logs(
    current_user: Annotated[User, Depends(require_permissions("audit:read"))],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 100,
):
    limit = min(max(limit, 1), 500)
    logs = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all()
    return ok([serialize_audit_log(log) for log in logs])


def serialize_audit_log(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "actor_id": log.actor_id,
        "action": log.action,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "detail": log.detail,
        "metadata_json": log.metadata_json,
        "created_at": log.created_at,
    }
