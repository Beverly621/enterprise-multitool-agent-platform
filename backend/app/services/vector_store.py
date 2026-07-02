from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.services.chunk_service import TextChunk
from app.services.embedding_service import embed_texts


@dataclass(slots=True)
class VectorSearchResult:
    chunk_id: int
    document_id: int
    filename: str
    chunk_index: int
    content: str
    score: float
    metadata: dict[str, Any] | None


class VectorStore:
    def __init__(self, db: Session):
        self.db = db

    def replace_document_chunks(self, document: Document, chunks: list[TextChunk]) -> int:
        self.db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        embeddings = embed_texts([chunk.content for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            self.db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    embedding=embedding,
                    metadata_json=chunk.metadata,
                )
            )
        document.chunk_count = len(chunks)
        return len(chunks)

    def similarity_search(
        self,
        kb_id: int,
        query: str,
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        query_embedding = embed_texts([query])[0]
        distance = DocumentChunk.embedding.l2_distance(query_embedding)
        statement = (
            select(DocumentChunk, Document, distance.label("distance"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.kb_id == kb_id)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )
        if metadata_filter:
            statement = statement.where(DocumentChunk.metadata_json.contains(metadata_filter))

        results: list[VectorSearchResult] = []
        for chunk, document, raw_distance in self.db.execute(statement).all():
            distance_value = float(raw_distance or 0)
            results.append(
                VectorSearchResult(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    filename=document.filename,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    score=1 / (1 + distance_value),
                    metadata=chunk.metadata_json,
                )
            )
        return results
