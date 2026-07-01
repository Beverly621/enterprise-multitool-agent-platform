from app.agent.state import AgentState


def build_agent_graph():
    """Placeholder for the LangGraph planner introduced in later phases."""
    return None


def run_agent_once(state: AgentState) -> AgentState:
    return {**state, "final_answer": "Agent planner is scheduled for a later phase."}

