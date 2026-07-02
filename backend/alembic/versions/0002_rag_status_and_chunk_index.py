"""rag status and chunk uniqueness

Revision ID: 0002_rag_status_and_chunk_index
Revises: 0001_initial_schema
Create Date: 2026-07-02
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0002_rag_status_and_chunk_index"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("documents", "status", server_default="UPLOADED")
    op.execute("UPDATE documents SET status = upper(status) WHERE status = lower(status)")
    op.create_unique_constraint(
        "uq_document_chunks_index",
        "document_chunks",
        ["document_id", "chunk_index"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_document_chunks_index", "document_chunks", type_="unique")
    op.alter_column("documents", "status", server_default="uploaded")
