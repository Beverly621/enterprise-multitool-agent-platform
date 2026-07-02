"""tool calling platform

Revision ID: 0004_tool_calling_platform
Revises: 0003_sql_agent_demo_tables
Create Date: 2026-07-02
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_tool_calling_platform"
down_revision: str | None = "0003_sql_agent_demo_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_tools",
        sa.Column("require_approval", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "agent_tools",
        sa.Column("permission_level", sa.String(length=32), nullable=False, server_default="User"),
    )
    op.add_column(
        "agent_tools",
        sa.Column("timeout_ms", sa.Integer(), nullable=False, server_default="5000"),
    )
    op.add_column(
        "agent_tools",
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "agent_tools",
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("agent_tools", sa.Column("created_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_agent_tools_created_by_users",
        "agent_tools",
        "users",
        ["created_by"],
        ["id"],
    )

    op.add_column("tool_calls", sa.Column("tool_call_id", sa.String(length=64), nullable=True))
    op.add_column("tool_calls", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("tool_calls", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column(
        "tool_calls",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.execute("UPDATE tool_calls SET tool_call_id = 'tc_' || id WHERE tool_call_id IS NULL")
    op.alter_column("tool_calls", "tool_call_id", nullable=False)
    op.alter_column("tool_calls", "run_id", nullable=True)
    op.create_index("ix_tool_calls_tool_call_id", "tool_calls", ["tool_call_id"], unique=True)
    op.create_index("ix_tool_calls_user_id", "tool_calls", ["user_id"])
    op.create_foreign_key("fk_tool_calls_user_id_users", "tool_calls", "users", ["user_id"], ["id"])

    op.add_column("approvals", sa.Column("approval_id", sa.String(length=64), nullable=True))
    op.add_column("approvals", sa.Column("tool_call_id", sa.String(length=64), nullable=True))
    op.add_column("approvals", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("approvals", sa.Column("tool_name", sa.String(length=128), nullable=True))
    op.add_column("approvals", sa.Column("approval_type", sa.String(length=64), nullable=True))
    op.add_column("approvals", sa.Column("requested_by", sa.Integer(), nullable=True))
    op.add_column("approvals", sa.Column("approved_by", sa.Integer(), nullable=True))
    op.add_column("approvals", sa.Column("request_payload", postgresql.JSONB(), nullable=True))
    op.add_column("approvals", sa.Column("approval_result", postgresql.JSONB(), nullable=True))
    op.add_column(
        "approvals",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.add_column("approvals", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("approvals", sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE approvals SET approval_id = 'ap_' || id WHERE approval_id IS NULL")
    op.alter_column("approvals", "approval_id", nullable=False)
    op.create_index("ix_approvals_approval_id", "approvals", ["approval_id"], unique=True)
    op.create_index("ix_approvals_tool_call_id", "approvals", ["tool_call_id"])
    op.create_foreign_key("fk_approvals_user_id_users", "approvals", "users", ["user_id"], ["id"])
    op.create_foreign_key(
        "fk_approvals_requested_by_users",
        "approvals",
        "users",
        ["requested_by"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_approvals_approved_by_users",
        "approvals",
        "users",
        ["approved_by"],
        ["id"],
    )

    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("todo_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="MEDIUM"),
        sa.Column("source_run_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_todos_todo_id", "todos", ["todo_id"], unique=True)
    op.create_index("ix_todos_user_id", "todos", ["user_id"])
    op.create_index("ix_todos_source_run_id", "todos", ["source_run_id"])

    op.create_table(
        "email_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("draft_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("to_email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="WAITING_APPROVAL",
        ),
        sa.Column("source_run_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_email_drafts_draft_id", "email_drafts", ["draft_id"], unique=True)
    op.create_index("ix_email_drafts_user_id", "email_drafts", ["user_id"])
    op.create_index("ix_email_drafts_source_run_id", "email_drafts", ["source_run_id"])


def downgrade() -> None:
    op.drop_table("email_drafts")
    op.drop_table("todos")
    for name in (
        "fk_approvals_approved_by_users",
        "fk_approvals_requested_by_users",
        "fk_approvals_user_id_users",
    ):
        op.drop_constraint(name, "approvals", type_="foreignkey")
    op.drop_index("ix_approvals_tool_call_id", table_name="approvals")
    op.drop_index("ix_approvals_approval_id", table_name="approvals")
    for column in (
        "rejected_at",
        "approved_at",
        "updated_at",
        "approval_result",
        "request_payload",
        "approved_by",
        "requested_by",
        "approval_type",
        "tool_name",
        "user_id",
        "tool_call_id",
        "approval_id",
    ):
        op.drop_column("approvals", column)
    op.drop_constraint("fk_tool_calls_user_id_users", "tool_calls", type_="foreignkey")
    op.drop_index("ix_tool_calls_user_id", table_name="tool_calls")
    op.drop_index("ix_tool_calls_tool_call_id", table_name="tool_calls")
    for column in ("updated_at", "error_message", "user_id", "tool_call_id"):
        op.drop_column("tool_calls", column)
    op.drop_constraint("fk_agent_tools_created_by_users", "agent_tools", type_="foreignkey")
    for column in (
        "created_by",
        "enabled",
        "retry_count",
        "timeout_ms",
        "permission_level",
        "require_approval",
    ):
        op.drop_column("agent_tools", column)
