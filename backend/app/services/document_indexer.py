from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.chunk_service import chunk_text
from app.services.document_parser import parse_document_file
from app.services.vector_store import VectorStore


def index_document(db: Session, document_id: int) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    try:
        document.status = "PARSING"
        document.updated_at = datetime.now(UTC)
        db.commit()

        parsed = parse_document_file(document.file_path)
        document.status = "CHUNKING"
        document.updated_at = datetime.now(UTC)
        db.commit()

        chunks = chunk_text(parsed.text, base_metadata=parsed.metadata)
        document.status = "EMBEDDING"
        document.updated_at = datetime.now(UTC)
        db.flush()

        VectorStore(db).replace_document_chunks(document, chunks)
        document.status = "READY"
        document.error_message = None
        document.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(document)
        return document
    except Exception as exc:
        db.rollback()
        document = db.get(Document, document_id)
        if document is not None:
            document.status = "FAILED"
            document.error_message = str(exc)
            document.updated_at = datetime.now(UTC)
            db.commit()
        raise
