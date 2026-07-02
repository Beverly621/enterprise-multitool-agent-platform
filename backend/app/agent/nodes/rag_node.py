from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.models.user import User
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.kb_permissions import get_accessible_kb
from app.services.provider_base import ChatMessage
from app.services.provider_factory import get_llm_provider
from app.services.rag_service import semantic_search


def run_rag_node(db: Session, run: AgentRun, state: AgentState, user: User) -> AgentState:
    started = datetime.now(UTC)
    kb_id = state.get("kb_id")
    if kb_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="kb_id is required")
    mark_run(db, run, "RETRIEVING", "RAG_RETRIEVAL")
    add_trace(db, run.run_id, "RAG_NODE_STARTED", metadata_json={"kb_id": kb_id})
    get_accessible_kb(db, int(kb_id), user)
    result = semantic_search(db, int(kb_id), state["query"], top_k=5)
    chunks = [chunk.model_dump() for chunk in result.retrieved_chunks]
    citations = [citation.model_dump() for citation in result.citations]
    context = "\n\n".join(chunk["content"] for chunk in chunks[:5]) or "No context retrieved."
    answer = get_llm_provider().chat(
        [
            ChatMessage(role="system", content="Answer from enterprise knowledge base context."),
            ChatMessage(role="user", content=f"Question: {state['query']}\n\nContext:\n{context}"),
        ]
    )
    if answer.startswith("[MockLLM]"):
        answer = "根据知识库检索结果，建议参考相关制度内容，并保留必要的引用依据。"
    state["retrieved_chunks"] = chunks
    state["citations"] = citations
    state["rag_answer"] = answer
    add_step(
        db,
        run.run_id,
        "RAG_RETRIEVAL",
        "rag",
        "SUCCESS",
        input_json={"kb_id": kb_id, "query": state["query"]},
        output_json={"chunk_count": len(chunks), "citation_count": len(citations)},
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(
        db,
        run.run_id,
        "RAG_NODE_FINISHED",
        metadata_json={"chunk_count": len(chunks), "citation_count": len(citations)},
    )
    return state
