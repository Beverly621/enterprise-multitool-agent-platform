from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.task_progress import TaskProgress
from app.models.user import User
from app.services.agent_step_service import add_trace
from app.services.tool_permission_service import highest_role_level

TERMINAL_TASK_STATUSES = {"SUCCESS", "FAILED", "CANCELLED", "TIMEOUT"}


def create_task_progress(
    db: Session,
    task_id: str,
    run_id: str | None,
    user_id: int | None,
    task_type: str,
    message: str = "Task submitted.",
) -> TaskProgress:
    progress = TaskProgress(
        task_id=task_id,
        run_id=run_id,
        user_id=user_id,
        task_type=task_type,
        status="PENDING",
        progress=0,
        current_stage="CREATED",
        message=message,
        updated_at=datetime.now(UTC),
    )
    db.add(progress)
    db.flush()
    return progress


def update_task_progress(
    db: Session,
    task_id: str,
    status: str,
    progress: int,
    current_stage: str,
    message: str | None = None,
    error_message: str | None = None,
) -> TaskProgress:
    task = get_task_progress(db, task_id)
    task.status = status
    task.progress = min(max(progress, 0), 100)
    task.current_stage = current_stage
    task.message = message
    task.error_message = error_message
    now = datetime.now(UTC)
    if status == "RUNNING" and task.started_at is None:
        task.started_at = now
    if status in TERMINAL_TASK_STATUSES or status == "WAITING_APPROVAL":
        task.finished_at = now if status in TERMINAL_TASK_STATUSES else None
    task.updated_at = now
    db.flush()
    if task.run_id:
        add_trace(
            db,
            task.run_id,
            "TASK_PROGRESS_UPDATED",
            event_type="task",
            metadata_json={
                "task_id": task_id,
                "status": status,
                "progress": task.progress,
                "current_stage": current_stage,
            },
        )
    return task


def get_task_progress(db: Session, task_id: str) -> TaskProgress:
    task = db.scalar(select(TaskProgress).where(TaskProgress.task_id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def get_run_progress(db: Session, run_id: str) -> TaskProgress:
    task = db.scalar(
        select(TaskProgress).where(TaskProgress.run_id == run_id).order_by(TaskProgress.id.desc())
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run progress not found")
    return task


def ensure_task_access(task: TaskProgress, user: User) -> None:
    if highest_role_level(user) >= 3 or task.user_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to task")


def serialize_task_progress(task: TaskProgress) -> dict:
    return {
        "run_id": task.run_id,
        "task_id": task.task_id,
        "task_type": task.task_type,
        "status": task.status,
        "progress": task.progress,
        "current_stage": task.current_stage,
        "message": task.message,
        "error_message": task.error_message,
        "started_at": task.started_at,
        "updated_at": task.updated_at,
        "finished_at": task.finished_at,
    }


def cancel_task_progress(db: Session, task: TaskProgress, user: User) -> TaskProgress:
    ensure_task_access(task, user)
    if task.status in TERMINAL_TASK_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is already {task.status} and cannot be cancelled.",
        )
    task.status = "CANCELLED"
    task.current_stage = "CANCELLED"
    task.message = "Task has been cancelled."
    task.error_message = None
    task.finished_at = datetime.now(UTC)
    task.updated_at = datetime.now(UTC)
    if task.run_id:
        run = db.scalar(select(AgentRun).where(AgentRun.run_id == task.run_id))
        if run is not None:
            run.status = "CANCELLED"
            run.current_step = "CANCELLED"
            run.finished_at = datetime.now(UTC)
            run.updated_at = datetime.now(UTC)
        add_trace(
            db,
            task.run_id,
            "TASK_CANCEL_REQUESTED",
            event_type="task",
            metadata_json={"task_id": task.task_id, "user_id": user.id},
        )
        add_trace(
            db,
            task.run_id,
            "TASK_CANCELLED",
            event_type="task",
            metadata_json={"task_id": task.task_id},
        )
    db.flush()
    return task
