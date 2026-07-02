# Enterprise Multi-Tool Agent Platform

企业级多工具知识库 Agent 平台，面向企业内部知识库、结构化数据库和业务 API 的 AI-Agent 后端与管理控制台。

当前完成阶段：**阶段七：前端后台与可视化控制台**。

## Phase Progress

| Phase | Scope | Status |
| --- | --- | --- |
| 1 | FastAPI, PostgreSQL + pgvector, Redis, Celery, JWT, RBAC, Alembic, Docker Compose | Done |
| 2 | RAG 文档解析、切分、Embedding、向量检索 | Done |
| 3 | SQL Agent 与 SQL Guardrails | Done |
| 4 | Tool Calling 与工具注册执行 | Done |
| 5 | Agent Planner 多步骤编排 | Done |
| 6 | 异步任务、任务进度、取消、幂等与报告历史 | Done |
| 7 | 前端后台、可视化控制台、权限菜单与演示页面 | Done |
| 8 | Demo 数据、公开资料接入与 GitHub 展示优化 | Planned |

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
- `GET /api/dashboard/summary`
- `GET /api/users`
- `GET /api/roles`
- `POST /api/roles`
- `POST /api/permissions/assign`
- `POST /api/kb`
- `GET /api/kb`
- `GET /api/kb/{id}`
- `GET /api/kb/{id}/documents`
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
- `GET /api/tool-calls`
- `POST /api/agent/chat`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/steps`
- `GET /api/runs/{run_id}/progress`
- `POST /api/runs/{run_id}/cancel`
- `GET /api/runs/{run_id}/tool-calls`
- `GET /api/runs/{run_id}/traces`
- `GET /api/tasks/{task_id}/progress`
- `GET /api/tasks`
- `POST /api/tasks/{task_id}/cancel`
- `GET /api/approvals`
- `GET /api/approvals/{approval_id}`
- `POST /api/approvals/{approval_id}/approve`
- `POST /api/approvals/{approval_id}/reject`
- `GET /api/reports`
- `GET /api/reports/{report_id}`
- `GET /api/runs/{run_id}/report`
- `POST /api/reports/{report_id}/export`

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

## Stage 5 Notes

- `POST /api/agent/chat` is the unified Agent Planner entrypoint for chat, RAG, SQL, tool calling, approval-required actions and multi-step reports.
- The planner supports `GENERAL_CHAT`, `RAG_QA`, `SQL_QUERY`, `TOOL_CALL`, `MULTI_STEP_REPORT` and `NEED_APPROVAL` intents.
- Planner nodes reuse the existing RAG service, SQL Agent and Tool Executor instead of bypassing guardrails.
- Multi-step reports execute SQL analysis first, optionally enrich with knowledge-base evidence, then render a structured Chinese report.
- Each planner run writes `agent_runs`, `agent_steps`, `agent_traces` and audit events so `/api/runs/{run_id}/steps` and `/api/runs/{run_id}/traces` can reconstruct the workflow.
- RBAC is enforced at the planner boundary: Guest can only use general chat and public RAG, User can use normal tools and reports, Developer can run SQL, and Admin can access all flows.

## Stage 6 Notes

- `POST /api/agent/chat` now supports `async_mode=true` and optional `idempotency_key`.
- Async submissions immediately return `run_id`, `task_id`, `progress_url` and `trace_url`; long work is executed by Celery.
- New tables store task progress, failed task dead-letter records, idempotency keys and Markdown report history.
- Users can query progress by run or task, and cancel non-terminal tasks cooperatively.
- Multi-step async reports are saved to `reports` with Markdown content and sanitized source metadata.
- Report export is reserved through `/api/reports/{report_id}/export` and currently returns a documented `not_implemented` placeholder.
- Celery worker imports all task modules explicitly and continues to work with Mock providers when real API keys are absent.

## Stage 7 Notes

- The frontend console now includes login, dashboard, knowledge-base management, Agent Chat, SQL Agent, tools, approvals, runs, tasks, reports, audit and admin users pages.
- Frontend auth uses localStorage token storage, automatic `Authorization: Bearer` headers, `/api/auth/me` session loading and 401 redirect to `/login`.
- The sidebar is role-aware: Guest, User, Developer and Admin see different navigation entries.
- Agent Chat supports sync and async mode, idempotency keys, progress polling, citations, generated SQL, tool results and approval IDs.
- Run detail pages show run metadata, final answer, step timeline, trace timeline, tool calls, task progress and linked reports.
- Lightweight backend console APIs were added for dashboard summary, task list, global tool call list, KB detail and KB documents.
- Frontend dependencies were upgraded to Next.js 16.2.10, React 19.2.0 and ESLint 9; `npm audit --omit=dev` reports zero vulnerabilities.
