from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    run_id: str
    user_id: int
    query: str
    intent: str
    steps: list[dict[str, Any]]
    final_answer: str

