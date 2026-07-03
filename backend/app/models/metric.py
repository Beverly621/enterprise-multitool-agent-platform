from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProviderCall(Base):
    __tablename__ = "provider_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    run_id: Mapped[str | None] = mapped_column(String(64), index=True)
    step_id: Mapped[int | None] = mapped_column(ForeignKey("agent_steps.id", ondelete="SET NULL"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(128))
    request_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    error_type: Mapped[str | None] = mapped_column(String(128))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvalCase(Base):
    __tablename__ = "eval_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    case_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    expected_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    tags: Mapped[list | None] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    eval_run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    case_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pass_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary_json: Mapped[dict | None] = mapped_column(JSONB)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    eval_run_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    case_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(8, 4), default=0, nullable=False)
    input_json: Mapped[dict | None] = mapped_column(JSONB)
    expected_json: Mapped[dict | None] = mapped_column(JSONB)
    actual_json: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RuntimeMetricsDaily(Base):
    __tablename__ = "runtime_metrics_daily"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date(), unique=True, index=True, nullable=False)
    agent_runs_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    agent_runs_success: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    agent_runs_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_run_duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rag_queries_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sql_queries_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sql_blocked_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tool_calls_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tool_calls_success: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tool_calls_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    async_tasks_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    async_tasks_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reports_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provider_calls_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_total_cost: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
