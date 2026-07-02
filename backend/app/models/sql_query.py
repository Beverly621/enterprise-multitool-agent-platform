from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SQLQueryLog(Base):
    __tablename__ = "sql_query_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    run_id: Mapped[str | None] = mapped_column(String(64), index=True)
    question: Mapped[str | None] = mapped_column(Text)
    natural_language_query: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[str | None] = mapped_column(Text)
    safe: Mapped[bool | None] = mapped_column(Boolean)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    is_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    guardrail_reason: Mapped[str | None] = mapped_column(Text)
    result_preview: Mapped[list | None] = mapped_column(JSONB)
    result_json: Mapped[dict | None] = mapped_column(JSONB)
    row_count: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
