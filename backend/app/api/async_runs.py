from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.task_progress_service import (
    cancel_task_progress,
    ensure_task_access,
    get_run_progress,
    get_task_progress,
    serialize_task_progress,
)

router = APIRouter()


@router.get("/runs/{run_id}/progress")
def run_progress(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    progress = get_run_progress(db, run_id)
    ensure_task_access(progress, current_user)
    return ok(serialize_task_progress(progress))


@router.get("/tasks/{task_id}/progress")
def task_progress(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    progress = get_task_progress(db, task_id)
    ensure_task_access(progress, current_user)
    return ok(serialize_task_progress(progress))


@router.post("/runs/{run_id}/cancel")
def cancel_run(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    progress = get_run_progress(db, run_id)
    task = cancel_task_progress(db, progress, current_user)
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="ASYNC_AGENT_RUN_CANCELLED",
            resource_type="agent_run",
            resource_id=run_id,
            metadata_json={"task_id": task.task_id},
        )
    )
    db.commit()
    return ok(
        {
            "run_id": task.run_id,
            "task_id": task.task_id,
            "status": task.status,
            "message": "Task has been cancelled.",
        }
    )


@router.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    progress = get_task_progress(db, task_id)
    task = cancel_task_progress(db, progress, current_user)
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="ASYNC_AGENT_RUN_CANCELLED",
            resource_type="task",
            resource_id=task_id,
            metadata_json={"run_id": task.run_id},
        )
    )
    db.commit()
    return ok(
        {
            "run_id": task.run_id,
            "task_id": task.task_id,
            "status": task.status,
            "message": "Task has been cancelled.",
        }
    )
