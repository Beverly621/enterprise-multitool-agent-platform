# Interview Q&A

This document prepares concise, implementation-grounded answers for interviews. The project uses simulated demo data and Mock providers by default; it is not presented as a live production deployment.

## Project Design

1. **What is this project?**  
   It is an enterprise-style multi-tool Agent platform built with FastAPI, Next.js, PostgreSQL/pgvector, Redis and Celery. It combines RAG, SQL Agent, Tool Calling, multi-step reports, RBAC, SQL Guardrails, tracing, audit logs, metrics and eval datasets.

2. **How is it different from a normal RAG chatbot?**  
   A normal RAG chatbot mainly retrieves documents and answers questions. This platform can also query structured demo order data, call registered tools, require human approval for sensitive actions, run async reports and preserve traces for debugging.

3. **What was your main responsibility?**  
   End-to-end implementation: backend APIs, database models, Agent runtime, RAG services, SQL Guardrails, tool execution, async tasks, frontend pages, demo data, tests, Docker, CI/CD and public documentation.

4. **Why did you choose this architecture?**  
   The split keeps the frontend, API, Agent runtime, background jobs and data layer independently testable. PostgreSQL stores both relational data and vectors, Redis/Celery handle long jobs, and FastAPI exposes typed APIs for the console.

5. **What is the core demo flow?**  
   Log in, inspect demo data, ask a RAG question, run a SQL Agent query, request a multi-step report, open Run Trace, review Reports, trigger an approval, then inspect Audit.

## RAG Design

6. **How does document ingestion work?**  
   Documents are parsed, chunked, embedded through a provider abstraction, stored in PostgreSQL with pgvector, and retrieved through the RAG service with citations.

7. **Why use a Mock embedding provider?**  
   It makes the public repo runnable in interviews and CI without real API keys while preserving the same code path and provider boundary.

8. **Where is RAG implemented?**  
   Key modules include `backend/app/services/document_parser.py`, `chunk_service.py`, `embedding_service.py`, `vector_store.py`, `rag_service.py`, and `backend/app/api/knowledge_base.py`.

9. **How do you evaluate RAG?**  
   Stage 9 adds JSONL eval cases in `backend/app/evals/rag_eval_cases.jsonl` and a runner through `python -m app.scripts.run_eval --type rag`.

10. **What would you improve in RAG next?**  
    Add richer file formats, hybrid search, reranking, chunk-quality analysis, Langfuse/OpenTelemetry export and larger eval sets.

## SQL Agent Design

11. **Why does the project include a SQL Agent?**  
    Enterprise questions often mix policy documents with structured business metrics. SQL Agent handles demo order analytics that pure RAG would not answer reliably.

12. **Why are SQL Guardrails necessary?**  
    Generated SQL can be unsafe. Guardrails restrict execution to read-only, allowlisted, limited queries and block destructive or sensitive access.

13. **How do you prevent access to sensitive tables or fields?**  
    The schema reader and guardrails enforce allowlists and deny sensitive table/field references before SQL is executed.

14. **Does the SQL Agent execute arbitrary user SQL?**  
    No. Queries pass through validation in `backend/app/services/sql_guardrails.py` and execution is handled by `sql_executor.py` under controlled rules.

15. **How is SQL Agent tested?**  
    Tests cover schema reading, SQL execution, guardrail blocking, API behavior and eval cases such as multi-statement SQL, DDL, `SELECT *`, sensitive fields and missing limits.

## Tool Calling Design

16. **What tools are included?**  
    Built-in tools cover knowledge search, safe SQL, order status lookup, after-sales lookup, report generation, email draft creation and todo creation.

17. **How are tools registered?**  
    Tool metadata, schemas, permissions and approval requirements are represented by the tool registry and related services under `backend/app/services/tool_registry.py`.

18. **Why does `send_email_draft` require approval?**  
    It represents an external or sensitive action. The project creates a draft and approval record instead of sending a real email.

19. **How do you validate tool arguments?**  
    Tool calls use JSON Schema-style metadata and validation services before execution.

20. **How are tool calls traced?**  
    Tool execution records are connected to agent runs, tool call logs and audit events.

## Agent Planner

21. **What intents can the Agent route?**  
    `GENERAL_CHAT`, `RAG_QA`, `SQL_QUERY`, `TOOL_CALL`, `MULTI_STEP_REPORT` and `NEED_APPROVAL`.

22. **Where is the planner implemented?**  
    Core files include `backend/app/agent/graph.py`, `backend/app/agent/nodes/`, `backend/app/services/planner_service.py` and `backend/app/services/agent_runtime.py`.

23. **How does a multi-step report work?**  
    The planner combines SQL analysis, RAG retrieval and report generation, then writes steps and traces for replay in the frontend.

24. **Why keep node boundaries explicit?**  
    It makes routing, trace output, tests and future replacement with LangGraph-style orchestration easier.

25. **What happens when the Agent cannot safely act?**  
    The system either returns a guarded refusal, creates an approval item, or routes to a safer intent depending on the workflow.

## Async Tasks

26. **Why use Celery?**  
    Reports and long Agent runs should not block HTTP requests. Celery with Redis allows progress tracking, retries and cancellation.

27. **Where are async tasks implemented?**  
    `backend/app/tasks/agent_tasks.py`, `report_tasks.py`, `task_progress_service.py`, `async_run_service.py` and task-related APIs.

28. **How does the frontend show progress?**  
    It reads task progress APIs and displays status through the Tasks and Reports pages.

29. **How is idempotency handled?**  
    Seed and task-related flows include idempotency checks so repeated demo setup does not duplicate core records unexpectedly.

30. **What would you improve for production async work?**  
    Add stronger retry policies, dead-letter handling, task scheduling dashboards and deployment-level monitoring.

## Security, Trace, Audit and Metrics

31. **How does RBAC work?**  
    JWT auth identifies the user, and role/permission services gate Admin, Developer, User and Guest access to APIs and tool actions.

32. **What security risks did you address?**  
    SQL injection/destructive SQL, accidental tool execution, secret leakage, public demo data safety, CORS configuration and frontend exposure of provider keys.

33. **What is recorded in traces?**  
    Agent runs, steps, node events, SQL/tool execution context, task progress and final outcomes where applicable.

34. **What is recorded in audit logs?**  
    Important user and security actions such as login, SQL queries, tool calls, approvals, report generation and eval events.

35. **How do metrics prove observability?**  
    Metrics APIs expose Agent success rate, latency, SQL blocks, RAG/tool/task counts, provider calls and eval results.

## Frontend Console

36. **What frontend pages exist?**  
    Login, Dashboard, Knowledge Base, Agent Chat, SQL Agent, Tools, Approvals, Runs, Tasks, Reports, Audit and Admin Users.

37. **How does the frontend avoid fake data?**  
    The pages call backend APIs from the real FastAPI service. Demo data is seeded into the backend instead of being hardcoded as production data.

38. **What is the most important frontend page for interviews?**  
    Agent Chat plus Runs/Trace, because they show the user request and how the system decomposed it.

39. **How do permissions affect the UI?**  
    Roles control visible actions and backend access; UI behavior is backed by API authorization rather than only client-side hiding.

40. **What would you improve in the UI?**  
    Add richer dashboards, better filtering, E2E tests, polished screenshots and live trace streaming.

## Deployment, CI/CD and Improvements

41. **How can reviewers run the project locally?**  
    Copy `.env.example`, copy `frontend/.env.example`, run `docker compose up -d --build`, then run `bash scripts/seed_demo_data.sh`.

42. **What does CI cover?**  
    Backend tests, frontend lint/build, Docker build, environment validation and public safety checks through GitHub Actions.

43. **Is the project deployed to production?**  
    The repository includes production-oriented deployment templates, but the documentation does not claim a live production deployment.

44. **How do you avoid leaking secrets on GitHub?**  
    `.env` files are ignored, provider keys are placeholders, `check_public_safety.sh` scans for tracked env files and high-confidence secret patterns, and frontend public variables never store model keys.

45. **What was the hardest technical challenge?**  
    Making RAG, SQL, tools, approvals and reports feel like one traceable Agent workflow while keeping each subsystem testable and safe.

46. **What is the biggest current limitation?**  
    The project is demo-oriented. Production use would need real provider configuration, stronger tenant isolation, SSO, monitoring, backups and operational runbooks.

47. **Why are eval datasets useful here?**  
    They turn core behaviors into repeatable checks: RAG retrieval, SQL safety, tool permission handling and Agent routing can be tested after changes.

48. **What would you do next if given more time?**  
    Add Langfuse/OpenTelemetry export, Playwright E2E, richer document ingestion, tenant isolation, enterprise SSO, workflow editing and production observability dashboards.
