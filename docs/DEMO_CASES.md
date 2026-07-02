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

## Stage 3 SQL Agent Demo

1. Seed demo orders with `docker compose exec backend python -m app.seed.seed_demo_orders`.
2. Call `GET /api/sql-agent/schema` and verify only `demo_*` tables are returned.
3. Ask `POST /api/sql-agent/query` with `哪个地区的异常订单最多？`.
4. Verify the response includes generated SQL, safe status, rows, answer and trace URL.
5. Try `DROP TABLE demo_orders。` and verify Guardrails block it.
