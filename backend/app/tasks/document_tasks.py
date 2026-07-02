from app.core.database import SessionLocal
from app.services.document_indexer import index_document
from app.tasks.celery_app import celery_app


@celery_app.task(name="documents.parse")
def parse_document(document_id: int) -> dict:
    with SessionLocal() as db:
        document = index_document(db, document_id)
        return {
            "document_id": document.id,
            "status": document.status,
            "chunk_count": document.chunk_count,
        }
