"""sql agent demo tables

Revision ID: 0003_sql_agent_demo_tables
Revises: 0002_rag_status_and_chunk_index
Create Date: 2026-07-02
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_sql_agent_demo_tables"
down_revision: str | None = "0002_rag_status_and_chunk_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "demo_customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.String(length=64), nullable=False),
        sa.Column("customer_name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("city", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_customers_customer_id", "demo_customers", ["customer_id"], unique=True)
    op.create_index("ix_demo_customers_state", "demo_customers", ["state"])

    op.create_table(
        "demo_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("department", sa.String(length=128), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_products_product_id", "demo_products", ["product_id"], unique=True)
    op.create_index("ix_demo_products_category", "demo_products", ["category"])

    op.create_table(
        "demo_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("customer_id", sa.String(length=64), nullable=False),
        sa.Column("order_status", sa.String(length=32), nullable=False),
        sa.Column("order_purchase_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_delivered_customer_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_estimated_delivery_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_value", sa.Float(), nullable=False),
        sa.Column("seller_id", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_orders_order_id", "demo_orders", ["order_id"], unique=True)
    op.create_index("ix_demo_orders_customer_id", "demo_orders", ["customer_id"])
    op.create_index("ix_demo_orders_order_status", "demo_orders", ["order_status"])
    op.create_index(
        "ix_demo_orders_order_purchase_timestamp",
        "demo_orders",
        ["order_purchase_timestamp"],
    )
    op.create_index("ix_demo_orders_seller_id", "demo_orders", ["seller_id"])
    op.create_index("ix_demo_orders_state", "demo_orders", ["state"])

    op.create_table(
        "demo_order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("seller_id", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("freight_value", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_order_items_order_id", "demo_order_items", ["order_id"])
    op.create_index("ix_demo_order_items_product_id", "demo_order_items", ["product_id"])
    op.create_index("ix_demo_order_items_seller_id", "demo_order_items", ["seller_id"])

    op.create_table(
        "demo_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("review_id", sa.String(length=64), nullable=False),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("review_score", sa.Integer(), nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_reviews_review_id", "demo_reviews", ["review_id"], unique=True)
    op.create_index("ix_demo_reviews_order_id", "demo_reviews", ["order_id"])
    op.create_index("ix_demo_reviews_review_score", "demo_reviews", ["review_score"])

    op.create_table(
        "demo_after_sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("after_sales_id", sa.String(length=64), nullable=False),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("issue_type", sa.String(length=64), nullable=False),
        sa.Column("issue_description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_demo_after_sales_after_sales_id",
        "demo_after_sales",
        ["after_sales_id"],
        unique=True,
    )
    op.create_index("ix_demo_after_sales_order_id", "demo_after_sales", ["order_id"])
    op.create_index("ix_demo_after_sales_issue_type", "demo_after_sales", ["issue_type"])
    op.create_index("ix_demo_after_sales_status", "demo_after_sales", ["status"])

    op.add_column("sql_query_logs", sa.Column("question", sa.Text(), nullable=True))
    op.add_column("sql_query_logs", sa.Column("safe", sa.Boolean(), nullable=True))
    op.add_column("sql_query_logs", sa.Column("blocked_reason", sa.Text(), nullable=True))
    op.add_column("sql_query_logs", sa.Column("result_preview", postgresql.JSONB(), nullable=True))
    op.add_column("sql_query_logs", sa.Column("row_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("sql_query_logs", "row_count")
    op.drop_column("sql_query_logs", "result_preview")
    op.drop_column("sql_query_logs", "blocked_reason")
    op.drop_column("sql_query_logs", "safe")
    op.drop_column("sql_query_logs", "question")

    for table_name in (
        "demo_after_sales",
        "demo_reviews",
        "demo_order_items",
        "demo_orders",
        "demo_products",
        "demo_customers",
    ):
        op.drop_table(table_name)
