# Demo Script

## 30-Second Introduction

Enterprise Multi-Tool Agent Platform is an enterprise-grade AI Agent platform that combines RAG document Q&A, SQL Agent analytics, Tool Calling, multi-step planning, async report generation, RBAC, SQL Guardrails, human approvals, tracing and audit logging. It includes Mock LLM and Mock Embedding providers, so the full demo can run locally without real API keys.

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

