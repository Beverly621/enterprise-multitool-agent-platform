from __future__ import annotations

from typing import Any

from app.core.database import SessionLocal
from app.services.failed_task_service import record_failed_task
from app.services.report_history_service import save_report_history
from app.services.report_service import render_report
from app.services.task_progress_service import create_task_progress, update_task_progress
from app.tasks.celery_app import celery_app


@celery_app.task(name="reports.generate")
def generate_report(run_id: str) -> dict:
    return {"run_id": run_id, "status": "queued"}


@celery_app.task(
    bind=True,
    name="reports.generate_async",
    max_retries=2,
    retry_backoff=True,
    retry_jitter=True,
)
def generate_report_async_task(
    self,
    run_id: str,
    user_id: int,
    report_payload: dict[str, Any],
) -> dict:
    db = SessionLocal()
    task_id = report_payload.get("task_id") or self.request.id
    try:
        create_task_progress(
            db,
            task_id=task_id,
            run_id=run_id,
            user_id=user_id,
            task_type="REPORT_GENERATION",
            message="Report generation submitted.",
        )
        update_task_progress(
            db,
            task_id,
            "RUNNING",
            80,
            "REPORT_GENERATION",
            "Generating markdown report.",
        )
        content = report_payload.get("content_markdown") or render_report(
            report_payload.get("title") or "业务分析报告",
            report_payload.get("sections") or ["## 一、数据来源\n- Not provided."],
        )
        report = save_report_history(
            db,
            run_id=run_id,
            user_id=user_id,
            title=report_payload.get("title") or "业务分析报告",
            report_type=report_payload.get("report_type") or "custom",
            content_markdown=content,
            source_metadata_json=report_payload.get("source_metadata_json"),
        )
        update_task_progress(
            db,
            task_id,
            "SUCCESS",
            100,
            "SUCCESS",
            "Report generation completed.",
        )
        db.commit()
        return {
            "run_id": run_id,
            "task_id": task_id,
            "report_id": report.report_id,
            "status": "SUCCESS",
        }
    except Exception as exc:
        db.rollback()
        record_failed_task(
            db,
            task_id=task_id,
            run_id=run_id,
            user_id=user_id,
            task_type="REPORT_GENERATION",
            error_message=str(exc),
            error_detail={"payload": report_payload},
            retry_count=self.request.retries,
            max_retry_count=2,
        )
        db.commit()
        if self.request.retries >= self.max_retries:
            return {"run_id": run_id, "task_id": task_id, "status": "FAILED"}
        raise self.retry(exc=exc) from exc
    finally:
        db.close()
