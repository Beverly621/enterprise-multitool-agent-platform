from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.agent_step_service import add_trace
from app.services.idempotency_service import (
    get_reusable_idempotency_key,
    request_hash,
    save_idempotency_key,
)
from app.services.task_progress_service import create_task_progress


def submit_async_agent_run(
    db: Session,
    user: User,
    query: str,
    session_id: str | None = None,
    kb_id: int | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    payload_hash = request_hash(
        {
            "query": query,
            "session_id": session_id,
            "kb_id": kb_id,
            "async_mode": True,
        }
    )
    if idempotency_key:
        existing = get_reusable_idempotency_key(db, user.id, idempotency_key, payload_hash)
        if existing is not None:
            return {
                "run_id": existing.run_id,
                "task_id": existing.task_id,
                "status": existing.status,
                "message": "Existing async agent task returned by idempotency key.",
                "progress_url": f"/api/runs/{existing.run_id}/progress",
                "trace_url": f"/api/runs/{existing.run_id}/traces",
                "idempotent": True,
            }

    run_id = f"run_{uuid.uuid4().hex}"
    task_id = f"task_{uuid.uuid4().hex}"
    run = AgentRun(
        run_id=run_id,
        user_id=user.id,
        session_id=session_id,
        query=query,
        intent="UNKNOWN",
        status="PENDING",
        current_step="ASYNC_SUBMITTED",
        updated_at=datetime.now(UTC),
    )
    db.add(run)
    db.flush()
    progress = create_task_progress(
        db,
        task_id=task_id,
        run_id=run_id,
        user_id=user.id,
        task_type="AGENT_RUN",
        message="Agent task has been submitted.",
    )
    add_trace(
        db,
        run_id,
        "ASYNC_TASK_SUBMITTED",
        event_type="task",
        metadata_json={"task_id": task_id, "kb_id": kb_id},
    )
    db.add(
        AuditLog(
            actor_id=user.id,
            action="ASYNC_AGENT_RUN_CREATED",
            resource_type="agent_run",
            resource_id=run_id,
            metadata_json={"task_id": task_id, "session_id": session_id},
        )
    )
    if idempotency_key:
        save_idempotency_key(
            db,
            user.id,
            idempotency_key,
            payload_hash,
            run_id,
            task_id,
            status_value=progress.status,
        )
    db.commit()

    from app.tasks.agent_tasks import run_agent_async_task

    run_agent_async_task.apply_async(
        args=[run_id, user.id, {"kb_id": kb_id, "task_id": task_id}],
        task_id=task_id,
    )
    return {
        "run_id": run_id,
        "task_id": task_id,
        "status": progress.status,
        "message": "Agent task has been submitted.",
        "progress_url": f"/api/runs/{run_id}/progress",
        "trace_url": f"/api/runs/{run_id}/traces",
        "idempotent": False,
    }
