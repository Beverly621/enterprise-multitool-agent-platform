from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.document import Document, DocumentChunk
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.services.provider_factory import get_embedding_provider

DEMO_DOCS = {
    "sample_company_policy.md": """
Sample Company Policy covers conflicts of interest, data security, approval workflows and customer
complaint handling. Employees must disclose vendor relationships, family-owned suppliers, side
businesses or personal benefits that may affect business decisions. Human approval is required for
AI-generated customer messages, data exports, refund overrides, SQL Guardrails overrides and external
report sharing. API keys, tokens, passwords, private database strings, payment data and raw customer
complaint records must not be sent outside approved systems.
""".strip(),
    "sample_after_sales_policy.md": """
Sample After-Sales Policy covers returns, delayed delivery, product damage, wrong items, refunds and
complaint escalation. Delayed delivery should be reviewed by carrier status, region, product
availability and repeated delay signals. Product damage cases should be escalated for electronics,
baby, health or food categories, repeated SKU issues or safety evidence. High-value refunds and manual
refund overrides require human review.
""".strip(),
    "sample_return_policy.md": """
Sample Return Policy defines returnable conditions, non-returnable conditions, refund time, abnormal
order handling and manual review. Abnormal orders include cancellation, unavailable inventory,
delivery delay, payment issue, low review score, refund request, damaged product, wrong item or
customer complaint. AI-generated customer communication must remain a draft until approved.
""".strip(),
    "sample_order_abnormal_handbook.md": """
Sample Order Abnormal Analysis Handbook defines canceled orders, unavailable inventory, delivery
delay, low review score, refund request, product damage, wrong item, payment issue and customer
complaint as abnormal signals. A report should include time range, abnormal order count, top regions,
top issue types, low-score category distribution, after-sales policy evidence, recommended actions and
traceable data sources.
""".strip(),
}


def seed(reset: bool = False) -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == "admin@example.com"))
        kb = db.scalar(select(KnowledgeBase).where(KnowledgeBase.name == "Enterprise Demo KB"))
        if kb is None:
            kb = KnowledgeBase(
                name="Enterprise Demo KB",
                description="Public demo knowledge base for local smoke tests.",
                owner_id=admin.id if admin else None,
                visibility="public",
            )
            db.add(kb)
            db.flush()

        if reset:
            documents = db.scalars(select(Document).where(Document.kb_id == kb.id)).all()
            for document in documents:
                db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
                db.delete(document)
            db.flush()

        embedding_provider = get_embedding_provider()
        created = 0
        for filename, content in DEMO_DOCS.items():
            document = db.scalar(select(Document).where(Document.kb_id == kb.id, Document.filename == filename))
            if document is not None:
                continue
            document = Document(
                kb_id=kb.id,
                filename=filename,
                file_type="md",
                file_path=f"data/demo_docs/{filename}",
                status="indexed",
                chunk_count=1,
            )
            db.add(document)
            db.flush()
            embedding = embedding_provider.embed([content])[0]
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=0,
                    content=content,
                    embedding=embedding,
                    metadata_json={"source": "seed_demo_data"},
                )
            )
            created += 1

        db.commit()
        print(f"Seeded demo knowledge base documents: {created or 'already up to date'}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    seed(reset=args.reset)
