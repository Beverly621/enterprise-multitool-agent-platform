# Observability and Eval

Stage 9 adds engineering assurance for metrics, provider calls, trace/audit standards, eval datasets, and regression checks.

## Metrics Data Model

- `provider_calls`: provider name, model, request type, status, latency, tokens, estimated cost and sanitized error.
- `eval_cases`: optional database metadata for reusable eval cases.
- `eval_runs`: aggregate execution record for each eval run.
- `eval_results`: per-case eval result with input, expected, actual and score.
- `runtime_metrics_daily`: reserved daily aggregate table for production rollups.

## Provider Calls

Mock and OpenAI providers record calls when a database metrics context is active. Mock calls always use `estimated_cost = 0`. Error messages are sanitized before storage and must not include API keys, authorization headers, tokens, secrets or passwords.

## Agent Run Metrics

`GET /api/metrics/agent-runs` returns total runs, success/failed/cancelled counts, success rate, average duration, P50/P95 duration, intent distribution, status distribution, recent failures and slow runs.

## RAG Eval

Dataset: `backend/app/evals/rag_eval_cases.jsonl`.

Metrics:

- `retrieval_hit`
- `keyword_match`
- `citation_present`
- `latency_ms`

Scoring: `retrieval_hit * 0.5 + keyword_match * 0.3 + citation_present * 0.2`.

Run:

```bash
cd backend
python -m app.scripts.run_eval --type rag
```

Use `--no-db` for local offline validation without writing eval tables.

## SQL Guardrails Eval

Dataset: `backend/app/evals/sql_guardrails_eval_cases.jsonl`.

It covers safe SELECT, mutating SQL, DDL, grants, `SELECT *`, multi statement SQL, sensitive tables, sensitive fields, missing LIMIT, large LIMIT, case bypass, comment bypass and subquery access to sensitive tables.

False negatives are blocking issues.

## Tool Eval

Dataset: `backend/app/evals/tool_eval_cases.jsonl`.

Checks tool existence, permissions, approval requirements and SQL Guardrails reuse for `execute_safe_sql`.

## Agent Regression

Datasets:

- `backend/app/evals/agent_eval_cases.jsonl`
- `backend/app/evals/regression_cases.jsonl`

They verify core demo intent routing and SQL safety behavior.

Run:

```bash
cd backend
python -m app.scripts.run_regression
```

## Trace Standard

Recommended event names:

- `AGENT_RUN_CREATED`
- `INTENT_ROUTER_STARTED`
- `INTENT_ROUTER_FINISHED`
- `RAG_NODE_STARTED`
- `RAG_NODE_FINISHED`
- `SQL_NODE_STARTED`
- `SQL_NODE_FINISHED`
- `TOOL_NODE_STARTED`
- `TOOL_NODE_FINISHED`
- `REPORT_NODE_STARTED`
- `REPORT_NODE_FINISHED`
- `ASYNC_TASK_SUBMITTED`
- `ASYNC_TASK_STARTED`
- `TASK_PROGRESS_UPDATED`
- `TASK_SUCCESS`
- `TASK_FAILED`
- `APPROVAL_REQUIRED`
- `APPROVAL_APPROVED`
- `APPROVAL_REJECTED`
- `FINAL_NODE_STARTED`
- `FINAL_NODE_FINISHED`
- `AGENT_RUN_SUCCESS`
- `AGENT_RUN_FAILED`

Trace metadata must be chronological, include enough node context to locate failures, include `duration_ms` where available, and never store raw secrets.

## Audit Standard

Recommended audit events:

- `LOGIN`
- `LOGOUT`
- `KB_CREATE`
- `DOCUMENT_UPLOAD`
- `RAG_QUERY`
- `SQL_AGENT_QUERY`
- `SQL_AGENT_BLOCKED`
- `TOOL_INVOKED`
- `TOOL_APPROVAL_CREATED`
- `TOOL_APPROVED`
- `TOOL_REJECTED`
- `AGENT_CHAT`
- `ASYNC_AGENT_RUN_CREATED`
- `TASK_CANCELLED`
- `REPORT_GENERATED`
- `REPORT_VIEWED`
- `EVAL_RUN_STARTED`
- `EVAL_RUN_FINISHED`

Security events must be audited, and audit metadata must use sanitized payloads.

## Metrics API

- `GET /api/metrics/summary`
- `GET /api/metrics/agent-runs`
- `GET /api/metrics/rag`
- `GET /api/metrics/sql-guardrails`
- `GET /api/metrics/tools`
- `GET /api/metrics/tasks`
- `GET /api/metrics/providers`
- `GET /api/evals/runs`
- `GET /api/evals/runs/{eval_run_id}`

Guest access is blocked. User access is scoped to personal metrics. Developer and Admin can view global engineering metrics and eval results.

## Frontend Dashboard

The existing Dashboard now displays Agent success rate, average/P95 run latency, RAG query count, SQL block count, tool success rate, async task success rate, reports generated, provider call count and estimated cost.

## Langfuse and OpenTelemetry Reservation

`provider_calls`, trace event names, and eval run IDs are intentionally structured so future Langfuse/OpenTelemetry exporters can map runs, spans and provider usage without changing core business tables.

## Safety Notes

- Do not commit `.env`, `.env.local` or real provider keys.
- Do not put model secrets in `NEXT_PUBLIC_*`.
- Do not store raw authorization headers, tokens, secrets, API keys or passwords in metrics, trace, audit or eval reports.
- Docker cold-start and container integration acceptance passed on 2026-07-03. Future changes to DB, Redis, Celery, API, frontend or seed behavior must preserve the same compose-based acceptance path.
