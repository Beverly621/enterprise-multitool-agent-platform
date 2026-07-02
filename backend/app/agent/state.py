from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    run_id: str
    user_id: int
    session_id: str | None
    query: str
    intent: str
    kb_id: int | None

    messages: list[dict[str, Any]]

    retrieved_chunks: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    rag_answer: str | None

    generated_sql: str | None
    sql_result: dict[str, Any] | None
    sql_answer: str | None

    selected_tool: str | None
    tool_args: dict[str, Any] | None
    tool_results: list[dict[str, Any]]

    report: str | None
    final_answer: str | None

    requires_approval: bool
    approval_id: str | None

    current_step: str
    error: str | None
    metadata: dict[str, Any]
    steps: list[dict[str, Any]]
