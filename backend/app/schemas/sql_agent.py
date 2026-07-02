from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SQLAgentQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


class SQLAgentQueryResponse(BaseModel):
    run_id: str
    question: str
    generated_sql: str | None = None
    safe: bool
    blocked_reason: str | None = None
    columns: list[str] = []
    rows: list[dict[str, Any]] = []
    row_count: int = 0
    duration_ms: int = 0
    answer: str
    trace_url: str


class SQLQueryLogRead(BaseModel):
    id: int
    run_id: str | None
    user_id: int | None
    question: str | None
    generated_sql: str | None
    safe: bool | None
    blocked_reason: str | None
    row_count: int | None
    duration_ms: int | None
    result_preview: list[dict[str, Any]] | None = None
    created_at: datetime | None = None
