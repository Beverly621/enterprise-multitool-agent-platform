from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import select

from app.agent.runtime import run_agent_chat_on_run
from app.core.database import SessionLocal
from app.models.agent_run import AgentRun
from app.models.user import User
from app.services.failed_task_service import record_failed_task
from app.services.idempotency_service import update_idempotency_status
from app.services.report_history_service import save_report_history
from app.services.task_progress_service import get_task_progress, update_task_progress
from app.tasks.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="agent.run_async",
    max_retries=2,
    retry_backoff=True,
    retry_jitter=True,
)
def run_agent_async_task(self, run_id: str, user_id: int, payload: dict[str, Any]) -> dict:
    task_id = payload.get("task_id") or self.request.id
    db = SessionLocal()
    try:
        task = get_task_progress(db, task_id)
        if task.status == "CANCELLED":
            return {"run_id": run_id, "task_id": task_id, "status": "CANCELLED"}
        user = db.scalar(select(User).where(User.id == user_id))
        run = db.scalar(select(AgentRun).where(AgentRun.run_id == run_id))
        if user is None or run is None:
            raise RuntimeError("Async agent task cannot find user or run.")

        update_task_progress(
            db,
            task_id,
            "RUNNING",
            10,
            "ROUTING",
            "Agent task started.",
        )
        db.commit()
        state = asyncio.run(run_agent_chat_on_run(db, user, run, kb_id=payload.get("kb_id")))
        task = get_task_progress(db, task_id)
        if task.status == "CANCELLED":
            return {"run_id": run_id, "task_id": task_id, "status": "CANCELLED"}

        if state.get("error"):
            _mark_task_failed(db, task_id, run_id, user_id, state["error"], self.request.retries)
            db.commit()
            return {"run_id": run_id, "task_id": task_id, "status": "FAILED"}

        if state.get("report"):
            save_report_history(
                db,
                run_id=run_id,
                user_id=user_id,
                title="业务分析报告",
                report_type="agent_multistep_report",
                content_markdown=state["report"],
                source_metadata_json={
                    "intent": state.get("intent"),
                    "citations": state.get("citations", []),
                    "generated_sql": state.get("generated_sql"),
                },
            )
        final_status = "WAITING_APPROVAL" if state.get("requires_approval") else "SUCCESS"
        progress_value = 95 if final_status == "WAITING_APPROVAL" else 100
        update_task_progress(
            db,
            task_id,
            final_status,
            progress_value,
            final_status,
            "Agent task is waiting for approval."
            if final_status == "WAITING_APPROVAL"
            else "Agent task completed.",
        )
        update_idempotency_status(db, task_id, final_status)
        db.commit()
        return {"run_id": run_id, "task_id": task_id, "status": final_status}
    except Exception as exc:
        db.rollback()
        try:
            _mark_task_failed(db, task_id, run_id, user_id, str(exc), self.request.retries)
            db.commit()
        finally:
            db.close()
        if self.request.retries >= self.max_retries or _is_non_retryable_error(str(exc)):
            return {"run_id": run_id, "task_id": task_id, "status": "FAILED"}
        raise self.retry(exc=exc) from exc
    finally:
        if db.is_active:
            db.close()


def _mark_task_failed(
    db,
    task_id: str,
    run_id: str,
    user_id: int,
    error_message: str,
    retry_count: int,
) -> None:
    update_task_progress(
        db,
        task_id,
        "FAILED",
        100,
        "FAILED",
        "Agent task failed.",
        error_message=error_message,
    )
    update_idempotency_status(db, task_id, "FAILED")
    record_failed_task(
        db,
        task_id=task_id,
        run_id=run_id,
        user_id=user_id,
        task_type="AGENT_RUN",
        error_message=error_message,
        error_detail={"run_id": run_id},
        retry_count=retry_count,
        max_retry_count=2,
    )


def _is_non_retryable_error(error_message: str) -> bool:
    lowered = error_message.lower()
    return any(
        marker in lowered
        for marker in (
            "requires developer",
            "forbidden",
            "guardrail",
            "not found",
            "cancelled",
            "approval",
            "validation",
        )
    )
