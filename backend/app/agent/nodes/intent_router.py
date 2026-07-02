from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.intent_router_service import route_intent


def run_intent_router_node(db: Session, run: AgentRun, state: AgentState) -> AgentState:
    started = datetime.now(UTC)
    mark_run(db, run, "ROUTING", "INTENT_ROUTER")
    add_trace(db, run.run_id, "INTENT_ROUTER_STARTED", content=state["query"])
    route = route_intent(state["query"])
    state["intent"] = route.intent
    state.setdefault("metadata", {})["intent"] = {
        "confidence": route.confidence,
        "reason": route.reason,
        "slots": route.slots,
    }
    add_step(
        db,
        run.run_id,
        "INTENT_ROUTER",
        "router",
        "SUCCESS",
        input_json={"query": state["query"]},
        output_json={
            "intent": route.intent,
            "confidence": route.confidence,
            "reason": route.reason,
            "slots": route.slots,
        },
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(
        db,
        run.run_id,
        "INTENT_ROUTER_FINISHED",
        metadata_json={"intent": route.intent, "confidence": route.confidence},
    )
    return state


def route_intent_legacy(query: str) -> str:
    return route_intent(query).intent
