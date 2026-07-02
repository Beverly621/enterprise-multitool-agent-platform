from typing import Any

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=128)
    query: str = Field(min_length=1, max_length=2000)
    kb_id: int | None = Field(default=None, ge=1)
    async_mode: bool = False
    idempotency_key: str | None = Field(default=None, max_length=128)


class AgentChatResponse(BaseModel):
    run_id: str
    intent: str | None = None
    status: str
    answer: str | None = None
    approval_id: str | None = None
    trace_url: str
    citations: list[dict[str, Any]] = []
    generated_sql: str | None = None
    sql_result: dict[str, Any] | None = None
    tool_results: list[dict[str, Any]] = []
    error: str | None = None
