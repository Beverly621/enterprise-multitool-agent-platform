# Demo Cases

## Stage 1

1. Start the stack with `docker compose up -d`.
2. Seed demo users with `docker compose exec backend python -m app.seed.seed_all`.
3. Open Swagger at http://localhost:8100/docs.
4. Log in as `admin@example.com` with `admin123`.
5. Call `/api/auth/me`, `/api/users` and `/api/roles` with the returned bearer token.

## Stage 2 RAG Demo

1. Create a public knowledge base with `POST /api/kb`.
2. Upload `data/sample_docs/platform_overview.md` with `POST /api/kb/{id}/documents`.
3. Wait for the document status to become `READY`.
4. Call `POST /api/kb/{id}/search` with a question about tracing or Celery.
5. Call `POST /api/chat/rag` and verify `answer`, `citations`, `retrieved_chunks` and `run_id`.
