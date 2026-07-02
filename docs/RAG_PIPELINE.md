# RAG Pipeline

Stage 2 implements the core RAG workflow.

## Flow

1. Create a knowledge base with `POST /api/kb`.
2. Upload PDF, DOCX, Markdown, TXT or CSV with `POST /api/kb/{id}/documents`.
3. Celery parses, chunks and embeds the document.
4. pgvector stores chunk embeddings in `document_chunks`.
5. `POST /api/kb/{id}/search` performs semantic TopK retrieval.
6. `POST /api/chat/rag` builds context, calls the configured LLM provider and returns citations.

## Defaults

- Chunk size: `800`
- Chunk overlap: `120`
- Mock embedding provider: deterministic local vectors
- Mock LLM provider: local response for complete offline demos
