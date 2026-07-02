from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user, get_user_permissions
from app.models.agent_run import AgentRun, AgentTrace
from app.models.user import User
from app.services.tool_executor import list_run_tool_calls, serialize_tool_call

router = APIRouter()


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
        select(AgentTrace).where(AgentTrace.run_id == run_id).order_by(AgentTrace.id)
    ).all()
    return ok([_serialize_trace(trace) for trace in traces])


def _ensure_run_access(db: Session, run_id: str, user: User) -> None:
    permissions = get_user_permissions(user)
    if "admin:*" in permissions or "traces:read" in permissions:
        return
    run = db.scalar(select(AgentRun).where(AgentRun.run_id == run_id))
    if run is None or run.user_id == user.id:
        return
    from fastapi import HTTPException, status

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to run traces")


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
