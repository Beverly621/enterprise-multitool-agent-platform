from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.final_answer_service import build_final_answer


def run_final_node(db: Session, run: AgentRun, state: AgentState) -> AgentState:
    started = datetime.now(UTC)
    if state.get("requires_approval"):
        status = "WAITING_APPROVAL"
    else:
        status = "SUCCESS"
    mark_run(db, run, "FINALIZING", "FINAL_ANSWER")
    add_trace(db, run.run_id, "FINAL_NODE_STARTED")
    answer = build_final_answer(state)
    state["final_answer"] = answer
    run.final_answer = answer
    run.status = status
    run.current_step = "FINAL_ANSWER"
    run.finished_at = None if status == "WAITING_APPROVAL" else datetime.now(UTC)
    run.updated_at = datetime.now(UTC)
    add_step(
        db,
        run.run_id,
        "FINAL_ANSWER",
        "final",
        status,
        input_json={"intent": state.get("intent")},
        output_json={"answer": answer, "approval_id": state.get("approval_id")},
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(
        db,
        run.run_id,
        "FINAL_NODE_FINISHED",
        metadata_json={"status": status, "approval_id": state.get("approval_id")},
    )
    add_trace(db, run.run_id, "AGENT_RUN_SUCCESS" if status == "SUCCESS" else "APPROVAL_REQUIRED")
    return state
