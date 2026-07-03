from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.models.metric import EvalResult, EvalRun
from app.models.user import User
from app.services.tool_permission_service import highest_role_level

router = APIRouter()


@router.get("/runs")
def list_eval_runs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
):
    _require_developer(current_user)
    runs = db.scalars(select(EvalRun).order_by(EvalRun.id.desc()).limit(min(limit, 200))).all()
    return ok([_serialize_run(run) for run in runs])


@router.get("/runs/{eval_run_id}")
def eval_run_detail(
    eval_run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _require_developer(current_user)
    run = db.scalar(select(EvalRun).where(EvalRun.eval_run_id == eval_run_id))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eval run not found")
    results = db.scalars(
        select(EvalResult).where(EvalResult.eval_run_id == eval_run_id).order_by(EvalResult.id)
    ).all()
    return ok({**_serialize_run(run), "results": [_serialize_result(result) for result in results]})


def _require_developer(user: User) -> None:
    if highest_role_level(user) < 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Eval results require Developer role.")


def _serialize_run(run: EvalRun) -> dict:
    return {
        "eval_run_id": run.eval_run_id,
        "case_type": run.case_type,
        "status": run.status,
        "total_cases": run.total_cases,
        "passed_cases": run.passed_cases,
        "failed_cases": run.failed_cases,
        "pass_rate": float(run.pass_rate or 0),
        "duration_ms": run.duration_ms,
        "summary_json": run.summary_json,
        "created_at": run.created_at,
    }


def _serialize_result(result: EvalResult) -> dict:
    return {
        "case_id": result.case_id,
        "status": result.status,
        "score": float(result.score or 0),
        "input_json": result.input_json,
        "expected_json": result.expected_json,
        "actual_json": result.actual_json,
        "error_message": result.error_message,
        "duration_ms": result.duration_ms,
    }
