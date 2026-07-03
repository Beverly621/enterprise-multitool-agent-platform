# Architecture Explain

This document supports a 5-minute interview explanation. It describes implemented modules only and treats demo data as simulated.

## 1. Overall Architecture

The platform is split into a Next.js frontend console, a FastAPI backend, an Agent runtime, Celery workers, Redis, and PostgreSQL with pgvector. The backend owns auth, RBAC, knowledge bases, Agent orchestration, SQL Guardrails, tool execution, traces, audit logs, metrics and eval APIs.

## 2. Frontend Layer

`frontend/app` contains the routed console pages: Dashboard, Knowledge Base, Agent Chat, SQL Agent, Tools, Approvals, Runs, Tasks, Reports, Audit and Admin Users. `frontend/components` contains shared UI, API helpers and layout elements.

## 3. API Layer

`backend/app/api` exposes the HTTP surface. Examples include `agent_chat.py`, `knowledge_base.py`, `sql_agent.py`, `tools.py`, `approvals.py`, `runs.py`, `tasks.py`, `reports.py`, `audit.py`, `metrics.py` and `evals.py`.

## 4. Auth / RBAC Layer

`backend/app/core/security.py`, `backend/app/services/auth_service.py`, `rbac_service.py`, `tool_permission_service.py` and RBAC models enforce JWT authentication and role-based access for Admin, Developer, User and Guest.

## 5. Agent Planner Layer

`backend/app/agent/graph.py`, `backend/app/agent/nodes/` and planner/runtime services route prompts into `GENERAL_CHAT`, `RAG_QA`, `SQL_QUERY`, `TOOL_CALL`, `MULTI_STEP_REPORT` or `NEED_APPROVAL`. Explicit node boundaries make traces easier to inspect.

## 6. RAG Pipeline

Documents flow through parsing, chunking, embedding, vector storage and retrieval. Key modules are `document_parser.py`, `chunk_service.py`, `embedding_service.py`, `vector_store.py`, `document_indexer.py` and `rag_service.py`.

## 7. SQL Agent Pipeline

`schema_reader.py` exposes safe schema metadata, `sql_agent_service.py` prepares queries, `sql_guardrails.py` blocks risky SQL, `sql_executor.py` executes approved read-only queries, and `sql_result_explainer.py` summarizes results.

## 8. Tool Calling Layer

`tool_registry.py`, `tool_validation_service.py`, `tool_permission_service.py`, `tool_executor.py` and `approval_service.py` implement registry metadata, argument validation, RBAC, execution, retries/timeouts and approval creation.

## 9. Async Task Layer

Celery tasks live in `backend/app/tasks`. Agent and report jobs can run asynchronously, while `task_progress_service.py`, `async_run_service.py` and task APIs expose progress and status to the frontend.

## 10. Observability Layer

`tracing_service.py`, `metrics_service.py`, `provider_metrics_service.py`, metrics APIs and eval runners record agent runs, steps, provider calls, latency, SQL blocks, task outcomes and regression results.

## 11. Data Layer

PostgreSQL stores users, roles, knowledge bases, documents, chunks, demo orders, reports, tasks, tool calls, approvals, traces, audit logs and metrics. pgvector supports semantic retrieval.

## 12. Security Layer

Security controls include JWT, RBAC, SQL Guardrails, frontend public-env separation, Mock provider fallback, human approval, public safety scripts and CI checks that avoid committing secrets or generated artifacts.

## 13. Why This Design

The design keeps Agent behavior composable while preserving conventional engineering boundaries. The platform can be demoed without real keys, tested with deterministic datasets, and extended toward production without rewriting every subsystem.

## 14. Alternatives

- Use a managed vector database instead of pgvector for scale and dedicated retrieval operations.
- Use LangGraph directly for the planner if the project needs more complex graph editing.
- Use a workflow engine for long-running business processes.
- Use Langfuse/OpenTelemetry exporters for production trace analysis.

## 15. Expansion Direction

Short-term work should focus on richer document formats, E2E tests and trace exporters. Mid-term work should add multi-tenant isolation, SSO, stronger policy controls and richer dashboards. Long-term work can explore plugin marketplaces, multi-Agent collaboration and workflow editing.
