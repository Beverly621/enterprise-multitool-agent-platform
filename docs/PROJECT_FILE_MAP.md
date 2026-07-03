# Project File Map

## `backend/app/api`

- Purpose: FastAPI route modules.
- Core files: `agent_chat.py`, `knowledge_base.py`, `sql_agent.py`, `tools.py`, `approvals.py`, `runs.py`, `tasks.py`, `reports.py`, `audit.py`, `metrics.py`, `evals.py`.
- Capability: exposes auth, RAG, SQL Agent, Tool Calling, Agent runs, tasks, reports, audit, metrics and eval APIs.

## `backend/app/services`

- Purpose: business logic and integration boundaries.
- Core files: `rag_service.py`, `sql_guardrails.py`, `tool_executor.py`, `planner_service.py`, `report_service.py`, `metrics_service.py`, `provider_factory.py`.
- Capability: implements RAG, SQL safety, tools, planning, reports, metrics, providers and RBAC helpers.

## `backend/app/models`

- Purpose: SQLAlchemy database models.
- Core files: `user.py`, `rbac.py`, `document.py`, `demo_order.py`, `agent_run.py`, `tool.py`, `report.py`, `audit_log.py`, `metric.py`.
- Capability: stores users, permissions, KB data, orders, runs, traces, tool calls, reports, audit logs and metrics.

## `backend/app/tasks`

- Purpose: Celery background tasks.
- Core files: `celery_app.py`, `agent_tasks.py`, `report_tasks.py`, `document_tasks.py`, `embedding_tasks.py`.
- Capability: async Agent runs, reports, indexing, embeddings, retry and cleanup flows.

## `backend/app/agent`

- Purpose: Agent runtime, graph, state and nodes.
- Core files: `graph.py`, `runtime.py`, `state.py`, `nodes/intent_router.py`, `nodes/rag_node.py`, `nodes/sql_node.py`, `nodes/tool_node.py`, `nodes/report_node.py`.
- Capability: routes user prompts into chat, RAG, SQL, tools, approval and multi-step reports.

## `backend/app/evals`

- Purpose: JSONL evaluation datasets.
- Core files: `rag_eval_cases.jsonl`, `sql_guardrails_eval_cases.jsonl`, `tool_eval_cases.jsonl`, `agent_eval_cases.jsonl`, `regression_cases.jsonl`.
- Capability: repeatable RAG, SQL safety, tool and Agent regression checks.

## `frontend/app`

- Purpose: Next.js app routes.
- Core files: `dashboard/page.tsx`, `kb/page.tsx`, `agent/page.tsx`, `sql-agent/page.tsx`, `tools/page.tsx`, `approvals/page.tsx`, `runs/page.tsx`, `tasks/page.tsx`, `reports/page.tsx`, `audit/page.tsx`.
- Capability: user-facing console for real backend workflows.

## `frontend/components`

- Purpose: shared frontend UI and API helpers.
- Core files: layout, navigation, API client and reusable controls.
- Capability: consistent console behavior and API integration.

## `docs`

- Purpose: architecture, demo, deployment, eval, security and presentation docs.
- Core files: `DEMO_GUIDE.md`, `DEPLOYMENT.md`, `OBSERVABILITY_AND_EVAL.md`, `INTERVIEW_QA.md`, `FINAL_PRESENTATION_GUIDE.md`.
- Capability: helps reviewers understand, run and discuss the project.

## `scripts`

- Purpose: local validation and operational helpers.
- Core files: `seed_demo_data.sh`, `docker_smoke_test.sh`, `pre_deploy_check.sh`, `check_env.sh`, `check_public_safety.sh`.
- Capability: reproducible demo seed, Docker smoke test, pre-deploy validation and public safety scanning.

## `data/demo_docs`

- Purpose: self-written public-safe Markdown documents for RAG.
- Core files: company policy, after-sales policy, return policy and abnormal order handbook.
- Capability: local RAG demo without private enterprise data.

## `data/demo_orders`

- Purpose: simulated CSV order data.
- Core files: generated order, item, review and after-sales records.
- Capability: SQL Agent analytics demo.

## `deploy`

- Purpose: production-oriented deployment templates.
- Core files: `docker-compose.prod.yml`, `nginx.conf`, `render.yaml.example`, `fly.toml.example`, `railway.md`, `vercel.md`.
- Capability: deployment reference without real secrets.

## `.github/workflows`

- Purpose: GitHub Actions.
- Core files: backend CI, frontend CI, Docker build and public safety workflows.
- Capability: validates backend tests, frontend build, compose builds and public repository safety.
