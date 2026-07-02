from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.report_export_service import build_export_placeholder
from app.services.report_history_service import (
    get_report_for_user,
    get_run_report_for_user,
    list_reports,
    serialize_report,
)

router = APIRouter()


@router.get("/reports")
def reports(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 100,
):
    return ok([serialize_report(report) for report in list_reports(db, current_user, limit=limit)])


@router.get("/reports/{report_id}")
def report_detail(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    report = get_report_for_user(db, report_id, current_user)
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="REPORT_VIEWED",
            resource_type="report",
            resource_id=report.report_id,
            metadata_json={"run_id": report.run_id},
        )
    )
    db.commit()
    return ok(serialize_report(report))


@router.get("/runs/{run_id}/report")
def run_report(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    report = get_run_report_for_user(db, run_id, current_user)
    return ok(serialize_report(report))


@router.post("/reports/{report_id}/export")
def export_report(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    report = get_report_for_user(db, report_id, current_user)
    db.add(
        AuditLog(
            actor_id=current_user.id,
            action="REPORT_EXPORT_REQUESTED",
            resource_type="report",
            resource_id=report.report_id,
            metadata_json={"run_id": report.run_id},
        )
    )
    db.commit()
    return ok(build_export_placeholder(report))
