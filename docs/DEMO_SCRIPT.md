# Demo Script

## 30-Second Introduction

Enterprise Multi-Tool Agent Platform is an enterprise-grade AI Agent platform that combines RAG document Q&A, SQL Agent analytics, Tool Calling, multi-step planning, async report generation, RBAC, SQL Guardrails, human approvals, tracing and audit logging. It includes Mock LLM and Mock Embedding providers, so the full demo can run locally without real API keys.

## 1-Minute Resume Version

I built this as a portfolio-grade enterprise Agent platform rather than a single RAG chatbot. The backend is FastAPI with PostgreSQL/pgvector, Redis and Celery; the frontend is a Next.js console. The Agent can choose between knowledge retrieval, guarded SQL analytics, registered tools, human approval, and multi-step report generation. I also added tracing, audit logs, metrics, eval datasets, Docker Compose, CI workflows, and public-safe demo data so the project can be reviewed and run without private credentials.

## 2-Minute Demo Route

1. Log in as `admin@example.com`.
2. Show Dashboard metrics and navigation.
3. Open Knowledge Base and show demo policy documents.
4. Open Agent Chat.
5. Ask: `结合最近 30 天订单异常数据和售后知识库生成一份分析报告。`
6. Show async progress if enabled.
7. Open Run Trace and highlight SQL Node, RAG Node and Report Node.
8. Open Reports and show the Markdown report.
9. Trigger an email draft and show Approval.
10. Open Audit Log to show traceability.

## 5-Minute Technical Route

1. Explain the Next.js frontend and FastAPI backend split.
2. Explain Provider abstraction and Mock fallback.
3. Explain RAG ingestion and pgvector search.
4. Explain SQL Agent schema reading and Guardrails.
5. Explain Tool Registry, permission checks and approval flow.
6. Explain Agent Planner nodes and multi-step report orchestration.
7. Explain Celery async execution and progress APIs.
8. Explain Trace and Audit tables.

## 10-Minute Deep-Dive Route

1. Start from the README architecture diagram and clarify that the project is a local/demo-ready platform, not a live SaaS deployment.
2. Walk through `backend/app/agent/graph.py`, `backend/app/agent/nodes/`, and `backend/app/services/planner_service.py` to show intent routing and node boundaries.
3. Open `backend/app/services/rag_service.py`, `document_indexer.py`, `embedding_service.py`, and `vector_store.py` to explain document ingestion and retrieval.
4. Open `backend/app/services/sql_guardrails.py`, `schema_reader.py`, `sql_agent_service.py`, and `sql_executor.py` to explain how safe SQL is generated and constrained.
5. Open `backend/app/services/tool_registry.py`, `tool_executor.py`, and `approval_service.py` to show permission checks and human-in-the-loop handling.
6. Open `backend/app/tasks/agent_tasks.py` and `report_tasks.py` to explain async execution.
7. Open `backend/app/services/tracing_service.py`, `metrics_service.py`, and `provider_metrics_service.py` to explain observability.
8. Finish with `.github/workflows/`, `scripts/pre_deploy_check.sh`, and `scripts/docker_smoke_test.sh` to show production-readiness checks.

## Recording Steps

1. Start with the README and show the problem statement plus architecture diagram.
2. Open the frontend console and log in.
3. Show Dashboard, Knowledge Base, Agent Chat, SQL Agent, Runs, Reports, Approvals and Audit.
4. Run one RAG question, one SQL question and one multi-step report question.
5. Open the generated trace and report.
6. Trigger the email draft approval flow.
7. End by showing CI/CD, deployment docs and public safety check output.

## Page Focus

- Dashboard: overall system counters and observability summary.
- Knowledge Base: demo documents, upload flow and indexing state.
- Agent Chat: unified entry point for RAG, SQL, tools and multi-step reports.
- SQL Agent: generated SQL, Guardrails and result explanation.
- Tools: registered tool schemas, permission and approval metadata.
- Approvals: human review for sensitive actions such as email drafts.
- Runs: step-by-step Agent timeline and node outputs.
- Tasks: async progress, status and cancellation behavior.
- Reports: generated Markdown reports and history.
- Audit: login, SQL, tool, approval and Agent actions.

## Fallback Talk Track

- If Docker startup is slow, show the README, Demo Guide, smoke-test script and previous test result record, then run the frontend/backend checks that are already available locally.
- If the model provider is not configured, explain that Mock providers are the expected default for public demos and CI.
- If document upload is skipped during recording, use seeded demo data and explain where `data/demo_docs/` lives.
- If an approval item already exists, use it to explain the flow instead of recreating it live.

## Interview Follow-Up Points

- Why Mock providers are important for a public GitHub demo.
- How SQL Guardrails block dangerous queries.
- How RBAC affects Agent, SQL and Tool access.
- How human-in-the-loop approval prevents accidental external actions.
- How traces support debugging and demo replay.
- How the project can be extended with Langfuse or OpenTelemetry.

## Page Checklist

- Dashboard: platform summary.
- Knowledge Base: demo documents and indexing status.
- Agent Chat: multi-step report prompt.
- SQL Agent: generated guarded SQL.
- Runs: step and trace timeline.
- Tasks: async progress.
- Reports: generated Markdown report.
- Approvals: email draft approval.
- Audit: security and operation records.
