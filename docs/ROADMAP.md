# Roadmap

## Completed

- RAG document QA with parsing, chunking, embedding abstraction and pgvector retrieval.
- SQL Agent with schema reading, guarded execution and result explanation.
- Tool Calling with registry metadata, validation, RBAC, timeouts, traces and approvals.
- Agent Planner with chat, RAG, SQL, tool, report and approval intents.
- Async tasks and reports with Celery, Redis, progress APIs and report history.
- Frontend console for dashboard, KB, Agent Chat, SQL Agent, tools, approvals, runs, tasks, reports, audit and users.
- Eval and metrics for RAG, SQL Guardrails, tools, Agent regression and provider calls.
- Docker Compose, production Compose template, GitHub Actions, pre-deploy checks and public safety scanning.
- Resume, interview, architecture, demo and final presentation materials.

## Short-Term Optimization

- Integrate Langfuse or OpenTelemetry export for traces and provider calls.
- Support more document formats and better parsing diagnostics.
- Enhance report export formats and report comparison.
- Add Playwright E2E tests for the main demo flow.

## Mid-Term Optimization

- Add multi-tenant isolation for data, users, tools and traces.
- Strengthen permission policies with a dedicated policy engine.
- Add enterprise SSO.
- Improve Dashboard filtering, drill-down and operational metrics.

## Long-Term Optimization

- Build a plugin marketplace for tools and Agent nodes.
- Add multi-Agent collaboration.
- Add a visual workflow editor.
- Add production-grade monitoring, alerting, backup/restore and incident runbooks.
