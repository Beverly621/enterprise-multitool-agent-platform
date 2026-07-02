from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.task_progress import FailedTask
from app.services.agent_step_service import add_trace, sanitize_payload


def record_failed_task(
    db: Session,
    task_id: str,
    run_id: str | None,
    user_id: int | None,
    task_type: str,
    error_message: str,
    error_detail: dict[str, Any] | None = None,
    retry_count: int = 0,
    max_retry_count: int = 2,
) -> FailedTask:
    failed = FailedTask(
        task_id=task_id,
        run_id=run_id,
        user_id=user_id,
        task_type=task_type,
        error_message=error_message,
        error_detail=sanitize_payload(error_detail),
        retry_count=retry_count,
        max_retry_count=max_retry_count,
        last_retry_at=datetime.now(UTC) if retry_count else None,
        status="OPEN",
    )
    db.add(failed)
    if run_id:
        add_trace(
            db,
            run_id,
            "TASK_FAILED",
            event_type="task",
            metadata_json={"task_id": task_id, "task_type": task_type, "error": error_message},
        )
    db.add(
        AuditLog(
            actor_id=user_id,
            action="TASK_FAILED_RECORDED",
            resource_type="task",
            resource_id=task_id,
            metadata_json={"run_id": run_id, "task_type": task_type},
        )
    )
    db.flush()
    return failed
