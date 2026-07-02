from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user, get_user_permissions
from app.models.sql_query import SQLQueryLog
from app.models.user import User
from app.schemas.sql_agent import SQLAgentQueryRequest
from app.services.schema_reader import read_allowed_schema
from app.services.sql_agent_service import run_sql_agent

router = APIRouter()


@router.get("/schema")
def get_demo_schema(current_user: Annotated[User, Depends(get_current_user)]):
    _require_sql_access(current_user)
    return ok(read_allowed_schema())


@router.post("/query")
def query_sql_agent(
    payload: SQLAgentQueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _require_sql_access(current_user)
    response = run_sql_agent(db, current_user, payload.question)
    return ok(response.model_dump())


@router.get("/logs")
def list_sql_query_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    permissions = get_user_permissions(current_user)
    if "admin:*" in permissions or "traces:read" in permissions:
        statement = select(SQLQueryLog).order_by(SQLQueryLog.id.desc()).limit(100)
    else:
        _require_sql_access(current_user)
        statement = (
            select(SQLQueryLog)
            .where(SQLQueryLog.user_id == current_user.id)
            .order_by(SQLQueryLog.id.desc())
            .limit(100)
        )
    return ok([_serialize_log(log) for log in db.scalars(statement).all()])


@router.get("/logs/{log_id}")
def get_sql_query_log(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    log = db.get(SQLQueryLog, log_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SQL query log not found")

    permissions = get_user_permissions(current_user)
    can_read = (
        "admin:*" in permissions
        or "traces:read" in permissions
        or log.user_id == current_user.id
    )
    if not can_read:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this SQL log",
        )
    return ok(_serialize_log(log))


def _require_sql_access(user: User) -> None:
    permissions = get_user_permissions(user)
    role_names = {role.name for role in user.roles}
    if (
        "admin:*" in permissions
        or "sql_agent:execute" in permissions
        or role_names & {"User", "Developer"}
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied: SQL Agent requires authenticated user role.",
    )


def _serialize_log(log: SQLQueryLog) -> dict:
    return {
        "id": log.id,
        "run_id": log.run_id,
        "user_id": log.user_id,
        "question": log.question or log.natural_language_query,
        "generated_sql": log.generated_sql,
        "safe": log.safe if log.safe is not None else log.is_allowed,
        "blocked_reason": log.blocked_reason or log.guardrail_reason,
        "row_count": log.row_count,
        "duration_ms": log.duration_ms,
        "result_preview": log.result_preview,
        "created_at": log.created_at,
    }
