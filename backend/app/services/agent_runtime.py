from app.agent.graph import run_agent_once
from app.agent.state import AgentState


def run_agent(state: AgentState) -> AgentState:
    return run_agent_once(state)

