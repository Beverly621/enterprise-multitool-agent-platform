from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.report import Report
from app.models.user import User
from app.services.agent_step_service import add_trace, sanitize_payload
from app.services.tool_permission_service import highest_role_level


def save_report_history(
    db: Session,
    run_id: str | None,
    user_id: int | None,
    title: str,
    content_markdown: str,
    report_type: str = "custom",
    summary: str | None = None,
    source_metadata_json: dict[str, Any] | None = None,
) -> Report:
    existing = None
    if run_id:
        existing = db.scalar(select(Report).where(Report.run_id == run_id))
    if existing is not None:
        return existing
    report = Report(
        report_id=f"report_{uuid.uuid4().hex}",
        run_id=run_id,
        user_id=user_id,
        title=title,
        report_type=report_type,
        content_markdown=content_markdown,
        summary=summary or _summary_from_markdown(content_markdown),
        source_metadata_json=sanitize_payload(source_metadata_json),
        status="READY",
    )
    db.add(report)
    if run_id:
        add_trace(
            db,
            run_id,
            "REPORT_SAVED",
            event_type="report",
            metadata_json={"report_id": report.report_id, "report_type": report_type},
        )
    db.add(
        AuditLog(
            actor_id=user_id,
            action="REPORT_GENERATED",
            resource_type="report",
            resource_id=report.report_id,
            metadata_json={"run_id": run_id, "report_type": report_type},
        )
    )
    db.flush()
    return report


def list_reports(db: Session, user: User, limit: int = 100) -> list[Report]:
    statement = select(Report).order_by(Report.id.desc()).limit(min(max(limit, 1), 500))
    if highest_role_level(user) < 3:
        statement = statement.where(Report.user_id == user.id)
    return list(db.scalars(statement).all())


def get_report_for_user(db: Session, report_id: str, user: User) -> Report:
    report = db.scalar(select(Report).where(Report.report_id == report_id))
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if highest_role_level(user) >= 3 or report.user_id == user.id:
        return report
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to report")


def get_run_report_for_user(db: Session, run_id: str, user: User) -> Report:
    report = db.scalar(select(Report).where(Report.run_id == run_id))
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if highest_role_level(user) >= 3 or report.user_id == user.id:
        return report
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to report")


def serialize_report(report: Report) -> dict:
    return {
        "id": report.id,
        "report_id": report.report_id,
        "run_id": report.run_id,
        "user_id": report.user_id,
        "title": report.title,
        "report_type": report.report_type,
        "content_markdown": report.content_markdown,
        "summary": report.summary,
        "source_metadata_json": report.source_metadata_json,
        "status": report.status,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


def _summary_from_markdown(markdown: str) -> str:
    plain_lines = []
    for line in markdown.splitlines():
        cleaned = line.strip().lstrip("#").lstrip("-").lstrip("*").strip()
        if cleaned:
            plain_lines.append(cleaned)
    return " ".join(plain_lines[:2])[:500] or "Generated report."
