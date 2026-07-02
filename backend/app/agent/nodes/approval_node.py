from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.services.agent_step_service import add_step, add_trace, mark_run


def run_approval_node(db: Session, run: AgentRun, state: AgentState) -> AgentState:
    if not state.get("requires_approval"):
        return state
    mark_run(db, run, "WAITING_APPROVAL", "APPROVAL_WAIT")
    add_step(
        db,
        run.run_id,
        "APPROVAL_WAIT",
        "approval",
        "WAITING_APPROVAL",
        input_json={"selected_tool": state.get("selected_tool")},
        output_json={"approval_id": state.get("approval_id")},
        started_at=datetime.now(UTC),
        ended_at=datetime.now(UTC),
    )
    add_trace(
        db,
        run.run_id,
        "APPROVAL_REQUIRED",
        metadata_json={"approval_id": state.get("approval_id")},
    )
    return state
