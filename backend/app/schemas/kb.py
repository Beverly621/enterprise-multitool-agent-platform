from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    description: str | None = None
    visibility: str = Field(default="private", pattern="^(private|public)$")


class KnowledgeBaseRead(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int | None
    visibility: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentRead(BaseModel):
    id: int
    kb_id: int
    filename: str
    file_type: str
    file_path: str
    status: str
    chunk_count: int
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    metadata_filter: dict[str, Any] | None = None


class Citation(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    score: float
    metadata: dict[str, Any] | None = None


class RetrievedChunk(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    chunk_index: int
    content: str
    score: float
    metadata: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    query: str
    top_k: int
    retrieved_chunks: list[RetrievedChunk]
    citations: list[Citation]
    results: list[dict[str, Any]] = []


class RAGRequest(BaseModel):
    query: str = Field(min_length=1)
    kb_id: int
    top_k: int = Field(default=5, ge=1, le=20)
    session_id: str | None = None


class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    run_id: str
