# Enterprise Multi-Tool Agent Platform

企业级多工具知识库 Agent 平台，面向企业内部知识库、结构化数据库和业务 API 的 AI-Agent 后端与管理控制台。

当前完成阶段：**阶段四：Tool Calling 平台**。

## Phase Progress

| Phase | Scope | Status |
| --- | --- | --- |
| 1 | FastAPI, PostgreSQL + pgvector, Redis, Celery, JWT, RBAC, Alembic, Docker Compose | Done |
| 2 | RAG 文档解析、切分、Embedding、向量检索 | Done |
| 3 | SQL Agent 与 SQL Guardrails | Done |
| 4 | Tool Calling 与工具注册执行 | Done |
| 5 | Agent Planner 多步骤编排 | Planned |
| 6 | Human-in-the-loop 审批与报告生成 | Planned |
| 7 | Tracing、审计与观测 | Planned |
| 8 | 前端后台完整演示与部署文档 | Planned |

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy 2.x, Pydantic
- Agent foundation: Provider abstraction with Mock/OpenAI implementations
- Database: PostgreSQL + pgvector
- Cache and queue: Redis, Celery
- Auth: JWT + RBAC
- Migration: Alembic
- Deploy: Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up -d
```

Open:

- Backend Swagger: http://localhost:8100/docs
- Health check: http://localhost:8100/health
- Frontend console: http://localhost:3100

Seed demo users after services are running:

```bash
docker compose exec backend python -m app.seed.seed_all
```

Demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@example.com | admin123 |
| Developer | developer@example.com | dev123 |
| User | user@example.com | user123 |
| Guest | guest@example.com | guest123 |

## Local Backend Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
python -m app.seed.seed_all
cd ..
bash scripts/run_backend.sh
```

For the frontend dev server, use `bash scripts/run_frontend.sh` and open http://localhost:3100.

Run backend tests:

```bash
cd backend
python -m pytest app/tests
```

## Implemented APIs

- `GET /health`
- `GET /api/version`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/users`
- `GET /api/roles`
- `POST /api/roles`
- `POST /api/permissions/assign`
- `POST /api/kb`
- `GET /api/kb`
- `POST /api/kb/{id}/documents`
- `GET /api/documents/{id}`
- `POST /api/kb/{id}/search`
- `POST /api/chat/rag`
- `GET /api/sql-agent/schema`
- `POST /api/sql-agent/query`
- `GET /api/sql-agent/logs`
- `GET /api/sql-agent/logs/{id}`
- `GET /api/tools`
- `GET /api/tools/{tool_name}`
- `POST /api/tools/register`
- `POST /api/tools/{tool_name}/enable`
- `POST /api/tools/{tool_name}/disable`
- `POST /api/tools/{tool_name}/invoke`
- `GET /api/tool-calls/{tool_call_id}`
- `GET /api/runs/{run_id}/tool-calls`
- `GET /api/approvals`
- `GET /api/approvals/{approval_id}`
- `POST /api/approvals/{approval_id}/approve`
- `POST /api/approvals/{approval_id}/reject`

## Stage 1 Notes

- PostgreSQL image uses `pgvector/pgvector:pg16`.
- Alembic migration creates `vector` extension and the initial schema.
- Missing LLM/Embedding API keys automatically fall back to Mock providers.
- JWT and RBAC are implemented with default Admin, Developer, User and Guest roles.
- `.env.example` contains no real API keys.

## Stage 2 Notes

- Supports PDF, DOCX, Markdown, TXT and CSV parsing.
- Document upload returns immediately and dispatches Celery indexing.
- Chunk defaults are `chunk_size=800` and `chunk_overlap=120`.
- Search uses PostgreSQL + pgvector and returns retrieved chunks plus citations.
- `POST /api/chat/rag` returns `answer`, `citations`, `retrieved_chunks` and `run_id`.

## Stage 3 Notes

- SQL Agent only exposes `demo_*` business tables through a safe Schema Reader.
- Demo e-commerce seed data includes 240 orders with abnormal statuses, delays, low scores and after-sales cases.
- SQL Guardrails allow only single-statement `SELECT`, block sensitive tables/fields, reject `SELECT *`, and clamp `LIMIT` to 100.
- Each SQL Agent query writes `agent_runs`, `agent_steps`, `agent_traces`, `sql_query_logs` and `audit_logs`.
- Mock SQL generation works without real LLM API keys and supports the recommended demo questions.

## Stage 4 Notes

- Built-in tools include RAG search, safe SQL execution, order status lookup, after-sales lookup, report generation, email draft approval and todo creation.
- Tool execution uses database-backed Registry metadata, JSON Schema argument validation, role hierarchy checks, timeout/retry handling and sanitized logging.
- `send_email_draft` never sends real email; it creates `email_drafts`, returns `WAITING_APPROVAL`, and requires `/api/approvals/{approval_id}/approve` or `/reject`.
- Tool calls write `tool_calls`, `agent_traces` and `audit_logs`; SQL execution tools still pass through SQL Guardrails.
