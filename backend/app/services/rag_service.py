import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun, AgentTrace
from app.schemas.kb import Citation, RAGResponse, RetrievedChunk, SearchResponse
from app.services.provider_base import ChatMessage
from app.services.provider_factory import get_llm_provider
from app.services.vector_store import VectorSearchResult, VectorStore


def semantic_search(
    db: Session,
    kb_id: int,
    query: str,
    top_k: int = 5,
    metadata_filter: dict | None = None,
) -> SearchResponse:
    results = VectorStore(db).similarity_search(kb_id, query, top_k, metadata_filter)
    return SearchResponse(
        query=query,
        top_k=top_k,
        retrieved_chunks=[_to_retrieved_chunk(result) for result in results],
        citations=[_to_citation(result) for result in results],
    )


def answer_with_rag(
    db: Session,
    user_id: int,
    kb_id: int,
    query: str,
    top_k: int = 5,
    session_id: str | None = None,
) -> RAGResponse:
    run_id = f"rag_{uuid.uuid4().hex}"
    run = AgentRun(
        run_id=run_id,
        user_id=user_id,
        session_id=session_id,
        query=query,
        intent="rag",
        status="running",
        current_step="retrieval",
    )
    db.add(run)
    db.flush()

    search_response = semantic_search(db, kb_id, query, top_k)
    context = _build_context(search_response.retrieved_chunks)
    prompt = (
        "You are an enterprise knowledge base assistant. Answer only from the context. "
        "When the context is insufficient, say what is missing.\n\n"
        f"Question:\n{query}\n\nContext:\n{context}"
    )
    started = datetime.now(UTC)
    answer = get_llm_provider().chat(
        [
            ChatMessage(
                role="system",
                content="Return a concise answer with business-friendly wording.",
            ),
            ChatMessage(role="user", content=prompt),
        ]
    )
    duration_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)

    run.status = "completed"
    run.current_step = "final"
    run.final_answer = answer
    run.finished_at = datetime.now(UTC)
    db.add(
        AgentTrace(
            run_id=run_id,
            event_type="rag",
            event_name="rag_answer",
            content=answer,
            metadata_json={"kb_id": kb_id, "top_k": top_k},
            duration_ms=duration_ms,
        )
    )
    db.commit()

    return RAGResponse(
        answer=answer,
        citations=search_response.citations,
        retrieved_chunks=search_response.retrieved_chunks,
        run_id=run_id,
    )


def _build_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant context retrieved."
    return "\n\n".join(
        f"[{index}] {chunk.filename}#chunk-{chunk.chunk_index}\n{chunk.content}"
        for index, chunk in enumerate(chunks, start=1)
    )


def _to_citation(result: VectorSearchResult) -> Citation:
    return Citation(
        document_id=result.document_id,
        filename=result.filename,
        chunk_id=result.chunk_id,
        chunk_index=result.chunk_index,
        score=result.score,
        metadata=result.metadata,
    )


def _to_retrieved_chunk(result: VectorSearchResult) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=result.chunk_id,
        document_id=result.document_id,
        filename=result.filename,
        chunk_index=result.chunk_index,
        content=result.content,
        score=result.score,
        metadata=result.metadata,
    )
