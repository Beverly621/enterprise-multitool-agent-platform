from app.agent.state import AgentState


def build_agent_graph():
    """LangGraph-compatible placeholder.

    Phase 5 uses a lightweight runtime while keeping this function as the future
    integration point for a LangGraph StateGraph.
    """
    return None


def run_agent_once(state: AgentState) -> AgentState:
    return {**state, "final_answer": state.get("final_answer") or "Agent planner runtime ready."}
