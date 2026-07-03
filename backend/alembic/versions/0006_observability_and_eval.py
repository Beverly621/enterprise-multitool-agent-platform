"""observability and eval

Revision ID: 0006_observability_and_eval
Revises: 0005_async_tasks_and_reports
Create Date: 2026-07-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_observability_and_eval"
down_revision: str | None = "0005_async_tasks_and_reports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "provider_calls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("call_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=True),
        sa.Column("step_id", sa.Integer(), sa.ForeignKey("agent_steps.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("provider_name", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=True),
        sa.Column("request_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost", sa.Numeric(12, 6), nullable=False, server_default="0"),
        sa.Column("error_type", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_provider_calls_call_id", "provider_calls", ["call_id"], unique=True)
    op.create_index("ix_provider_calls_run_id", "provider_calls", ["run_id"])
    op.create_index("ix_provider_calls_user_id", "provider_calls", ["user_id"])

    op.create_table(
        "eval_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(length=64), nullable=False),
        sa.Column("case_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input_json", postgresql.JSONB(), nullable=False),
        sa.Column("expected_json", postgresql.JSONB(), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_eval_cases_case_id", "eval_cases", ["case_id"], unique=True)
    op.create_index("ix_eval_cases_case_type", "eval_cases", ["case_type"])

    op.create_table(
        "eval_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("eval_run_id", sa.String(length=64), nullable=False),
        sa.Column("case_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("total_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pass_rate", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_eval_runs_eval_run_id", "eval_runs", ["eval_run_id"], unique=True)
    op.create_index("ix_eval_runs_case_type", "eval_runs", ["case_type"])

    op.create_table(
        "eval_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("eval_run_id", sa.String(length=64), nullable=False),
        sa.Column("case_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.Column("input_json", postgresql.JSONB(), nullable=True),
        sa.Column("expected_json", postgresql.JSONB(), nullable=True),
        sa.Column("actual_json", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_eval_results_eval_run_id", "eval_results", ["eval_run_id"])
    op.create_index("ix_eval_results_case_id", "eval_results", ["case_id"])

    op.create_table(
        "runtime_metrics_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("agent_runs_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("agent_runs_success", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("agent_runs_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_run_duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rag_queries_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sql_queries_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sql_blocked_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tool_calls_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tool_calls_success", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tool_calls_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("async_tasks_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("async_tasks_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reports_generated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provider_calls_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_total_cost", sa.Numeric(12, 6), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_runtime_metrics_daily_date", "runtime_metrics_daily", ["date"], unique=True)


def downgrade() -> None:
    op.drop_table("runtime_metrics_daily")
    op.drop_table("eval_results")
    op.drop_table("eval_runs")
    op.drop_table("eval_cases")
    op.drop_table("provider_calls")
