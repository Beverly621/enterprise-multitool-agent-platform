from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user, get_user_permissions
from app.models.agent_run import AgentRun, AgentStep, AgentTrace
from app.models.user import User
from app.services.tool_executor import list_run_tool_calls, serialize_tool_call

router = APIRouter()


@router.get("")
def list_runs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 100,
):
    limit = min(max(limit, 1), 500)
    statement = select(AgentRun).order_by(AgentRun.id.desc()).limit(limit)
    permissions = get_user_permissions(current_user)
    if "admin:*" not in permissions and "traces:read" not in permissions:
        statement = statement.where(AgentRun.user_id == current_user.id)
    runs = db.scalars(statement).all()
    return ok([_serialize_run(run) for run in runs])


@router.get("/{run_id}")
def run_detail(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    run = _get_run_for_user(db, run_id, current_user)
    return ok(_serialize_run(run))


@router.get("/{run_id}/steps")
def run_steps(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _ensure_run_access(db, run_id, current_user)
    steps = db.scalars(
        select(AgentStep).where(AgentStep.run_id == run_id).order_by(AgentStep.id)
    ).all()
    return ok([_serialize_step(step) for step in steps])


@router.get("/{run_id}/tool-calls")
def run_tool_calls(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ok([serialize_tool_call(item) for item in list_run_tool_calls(db, run_id, current_user)])


@router.get("/{run_id}/traces")
def run_traces(
    run_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    _ensure_run_access(db, run_id, current_user)
    traces = db.scalars(
        select(AgentTrace).where(AgentTrace.run_id == run_id).order_by(AgentTrace.created_at)
    ).all()
    return ok([_serialize_trace(trace) for trace in traces])


def _ensure_run_access(db: Session, run_id: str, user: User) -> None:
    _get_run_for_user(db, run_id, user, allow_missing=True)


def _get_run_for_user(
    db: Session,
    run_id: str,
    user: User,
    allow_missing: bool = False,
) -> AgentRun:
    permissions = get_user_permissions(user)
    if "admin:*" in permissions or "traces:read" in permissions:
        run = db.scalar(select(AgentRun).where(AgentRun.run_id == run_id))
        if run is not None or allow_missing:
            return run
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    run = db.scalar(select(AgentRun).where(AgentRun.run_id == run_id))
    if run is None:
        if allow_missing:
            return run
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.user_id == user.id:
        return run
    from fastapi import HTTPException, status

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to run traces")


def _serialize_run(run: AgentRun) -> dict:
    return {
        "id": run.id,
        "run_id": run.run_id,
        "user_id": run.user_id,
        "session_id": run.session_id,
        "query": run.query,
        "intent": run.intent,
        "status": run.status,
        "current_step": run.current_step,
        "final_answer": run.final_answer,
        "error_message": run.error_message,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
        "finished_at": run.finished_at,
    }


def _serialize_step(step: AgentStep) -> dict:
    return {
        "id": step.id,
        "run_id": step.run_id,
        "step_name": step.step_name,
        "step_type": step.step_type,
        "status": step.status,
        "input_json": step.input_json,
        "output_json": step.output_json,
        "error_message": step.error_message,
        "started_at": step.started_at,
        "ended_at": step.ended_at,
    }


def _serialize_trace(trace: AgentTrace) -> dict:
    return {
        "id": trace.id,
        "run_id": trace.run_id,
        "event_type": trace.event_type,
        "event_name": trace.event_name,
        "content": trace.content,
        "metadata_json": trace.metadata_json,
        "token_input": trace.token_input,
        "token_output": trace.token_output,
        "cost": trace.cost,
        "duration_ms": trace.duration_ms,
        "created_at": trace.created_at,
    }
