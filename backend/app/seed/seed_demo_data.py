from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.document import Document, DocumentChunk
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.services.provider_factory import get_embedding_provider


DEMO_DOC = """
Enterprise Multi-Tool Agent Platform supports RAG knowledge base Q&A, SQL Agent guarded data access,
tool calling, human approvals, tracing, Redis session cache and Celery asynchronous workloads.
""".strip()


def seed() -> None:
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

        document = db.scalar(select(Document).where(Document.filename == "platform_overview.md"))
        if document is None:
            document = Document(
                kb_id=kb.id,
                filename="platform_overview.md",
                file_type="md",
                file_path="data/sample_docs/platform_overview.md",
                status="indexed",
                chunk_count=1,
            )
            db.add(document)
            db.flush()
            embedding = get_embedding_provider().embed([DEMO_DOC])[0]
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=0,
                    content=DEMO_DOC,
                    embedding=embedding,
                    metadata_json={"source": "seed_demo_data"},
                )
            )

        db.commit()
        print("Seeded demo knowledge base.")


if __name__ == "__main__":
    seed()

