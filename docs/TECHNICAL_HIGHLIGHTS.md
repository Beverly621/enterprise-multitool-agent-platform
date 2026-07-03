# Technical Highlights

## 1. Multi-Tool Agent Runtime

- Problem: users may ask for chat, document retrieval, SQL analytics or tool actions in one interface.
- Implementation: `backend/app/agent/graph.py`, node modules and planner/runtime services route explicit intents.
- Value: keeps the user experience unified while preserving testable internal boundaries.

## 2. Unified RAG + SQL + Tool Orchestration

- Problem: enterprise tasks often need both unstructured and structured information.
- Implementation: multi-step report flows combine RAG, SQL Agent and report generation.
- Value: demonstrates a practical workflow beyond plain document QA.

## 3. SQL Guardrails

- Problem: generated SQL can leak data or mutate databases.
- Implementation: `backend/app/services/sql_guardrails.py` blocks unsafe operations, sensitive access, `SELECT *`, missing limits and multi-statement SQL.
- Value: turns SQL Agent into a safer analytics feature.

## 4. Human-in-the-Loop Approval

- Problem: tool calls can represent sensitive external actions.
- Implementation: approval services create review records for actions such as email drafts.
- Value: keeps automation auditable and reviewable before external side effects.

## 5. Async Agent Task

- Problem: reports and long Agent runs should not block HTTP requests.
- Implementation: Celery, Redis and task progress services process long workflows.
- Value: supports responsive APIs and frontend progress displays.

## 6. Full Traceability

- Problem: multi-step Agent behavior is hard to debug without history.
- Implementation: agent runs, steps, traces, tool logs, SQL logs and audit logs are persisted.
- Value: interviewers can inspect why a result happened instead of only seeing final text.

## 7. Mock Provider

- Problem: public projects should not require private model keys to run.
- Implementation: Mock LLM and embedding providers share the provider abstraction used by real providers.
- Value: makes local demos, CI and public review reproducible.

## 8. RBAC Permission System

- Problem: Admin, Developer, User and Guest should not share the same capabilities.
- Implementation: auth, RBAC services and permission checks protect APIs and tool execution.
- Value: mirrors enterprise access-control concerns.

## 9. Eval / Metrics

- Problem: Agent changes need repeatable quality and safety checks.
- Implementation: JSONL eval datasets, eval runners, regression runner and metrics APIs.
- Value: supports engineering assurance beyond manual demo testing.

## 10. Frontend Console

- Problem: backend-only demos are hard to understand quickly.
- Implementation: Next.js pages expose dashboard, KB, Agent Chat, SQL Agent, tools, approvals, traces, tasks, reports and audit.
- Value: makes the system visible and interview-friendly.

## 11. Docker + CI/CD

- Problem: reviewers need repeatable setup and maintainers need regression checks.
- Implementation: Docker Compose, production Compose template, pre-deploy script, smoke test and GitHub Actions.
- Value: reduces setup uncertainty and documents the path toward production deployment.
