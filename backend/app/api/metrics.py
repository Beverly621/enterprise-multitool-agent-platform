from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.user import User
from app.services import metrics_service
from app.services.tool_permission_service import highest_role_level

router = APIRouter()


@router.get("/summary")
def metrics_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.summary_metrics(db, _visible_user_id(current_user)))


@router.get("/agent-runs")
def agent_runs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.agent_run_metrics(db, _visible_user_id(current_user)))


@router.get("/rag")
def rag(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.rag_metrics(db, _visible_user_id(current_user)))


@router.get("/sql-guardrails")
def sql_guardrails(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.sql_guardrails_metrics(db, _visible_user_id(current_user)))


@router.get("/tools")
def tools(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.tool_metrics(db, _visible_user_id(current_user)))


@router.get("/tasks")
def tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.task_metrics(db, _visible_user_id(current_user)))


@router.get("/providers")
def providers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok(metrics_service.provider_metrics(db, _visible_user_id(current_user)))


def _visible_user_id(user: User) -> int | None:
    level = highest_role_level(user)
    if level <= 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Metrics require User role.")
    return None if level >= 2 else user.id
