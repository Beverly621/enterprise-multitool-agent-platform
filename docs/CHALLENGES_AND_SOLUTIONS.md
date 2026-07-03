# Challenges and Solutions

## 1. Running Without Real API Keys

- Problem: public reviewers may not have model provider credentials.
- Risk: the demo becomes impossible to run or secrets are accidentally committed.
- Solution: Mock LLM and embedding providers share the provider abstraction.
- Code / module: `mock_provider.py`, `provider_factory.py`, `.env.example`.
- Effect: local demo and CI can run without real API keys.
- Later optimization: add more provider adapters and trace exporters.

## 2. Preventing Dangerous SQL

- Problem: SQL Agent output can include mutation, DDL or sensitive access.
- Risk: data damage or leakage.
- Solution: enforce read-only Guardrails, sensitive denylist, limits and blocked patterns.
- Code / module: `sql_guardrails.py`, `sql_executor.py`, SQL tests and eval cases.
- Effect: unsafe SQL is rejected before execution.
- Later optimization: policy-driven schema scopes per tenant.

## 3. Orchestrating RAG, SQL and Tools

- Problem: one user request may require several capabilities.
- Risk: unstructured control flow becomes hard to debug.
- Solution: explicit planner intents and node-level execution.
- Code / module: `backend/app/agent/graph.py`, `backend/app/agent/nodes/`.
- Effect: the trace shows each step clearly.
- Later optimization: visual workflow editor or LangGraph replacement.

## 4. Handling Long Reports

- Problem: report generation can exceed a normal request lifecycle.
- Risk: request timeouts and poor UX.
- Solution: use Celery tasks, Redis and progress APIs.
- Code / module: `backend/app/tasks/agent_tasks.py`, `report_tasks.py`, `task_progress_service.py`.
- Effect: frontend can show task status while work continues.
- Later optimization: task queues by priority and dead-letter handling.

## 5. Tracking Tool Calls

- Problem: tool execution needs accountability.
- Risk: actions are hard to audit after the fact.
- Solution: persist tool calls, traces and audit events.
- Code / module: `tool_executor.py`, `tracing_service.py`, `audit.py`.
- Effect: reviewers can inspect what was called and why.
- Later optimization: richer per-tool latency and cost dashboards.

## 6. Designing Approval Flow

- Problem: some tool actions should not execute automatically.
- Risk: accidental external side effects.
- Solution: create approval records for sensitive actions such as email drafts.
- Code / module: `approval_service.py`, `approvals.py`, frontend approvals page.
- Effect: human review sits between Agent intent and sensitive execution.
- Later optimization: multi-approver policies.

## 7. Showing Real Backend State

- Problem: a frontend mock can look polished but prove little.
- Risk: interviewers cannot trust the workflow.
- Solution: pages call FastAPI endpoints backed by seeded data and real services.
- Code / module: `frontend/app`, `frontend/components`, `backend/app/api`.
- Effect: the console reflects backend state.
- Later optimization: Playwright E2E recordings.

## 8. Publishing Safely on GitHub

- Problem: public repos can accidentally include `.env`, logs or secrets.
- Risk: credential exposure and unsafe disclosure.
- Solution: `.gitignore`, `.env.example`, public safety script and CI workflow.
- Code / module: `scripts/check_public_safety.sh`, `.github/workflows/public-safety.yml`.
- Effect: common leak patterns are checked before publishing.
- Later optimization: add pre-commit secret scanning.

## 9. Keeping Demo Data Honest

- Problem: demo data can be mistaken for real enterprise data.
- Risk: misleading claims or privacy concerns.
- Solution: docs label data as simulated and public-safe.
- Code / module: `data/demo_docs`, `data/demo_orders`, `docs/PUBLIC_DATA_SOURCES.md`.
- Effect: the project remains suitable for public review.
- Later optimization: generate larger synthetic datasets on demand.
