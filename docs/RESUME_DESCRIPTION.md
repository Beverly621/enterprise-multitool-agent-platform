# Resume Description

## Chinese Resume Description

基于 FastAPI + Next.js + PostgreSQL/pgvector + Redis + Celery 设计并实现企业级多工具知识库 Agent 平台，支持 RAG 文档问答、SQL Agent 数据查询、Tool Calling、多步骤 Agent Planner、异步报告生成、RBAC 权限控制、SQL Guardrails、Human-in-the-loop 审批、Trace 与 Audit Log。系统内置 Mock LLM/Embedding Provider，在无真实 API Key 情况下也可本地完整运行 Demo。

## English Resume Description

Designed and implemented an enterprise-grade multi-tool AI Agent platform using FastAPI, Next.js, PostgreSQL/pgvector, Redis, and Celery. The platform supports RAG-based document QA, SQL Agent analytics, Tool Calling, multi-step Agent Planner workflows, asynchronous report generation, RBAC, SQL Guardrails, human-in-the-loop approvals, tracing, and audit logging. Built Mock LLM and Embedding providers to ensure the full demo can run locally without real API keys.

## Project Highlights

- Built a unified Agent Planner that routes general chat, RAG, SQL Agent, tool calls, multi-step reports and approval-required workflows.
- Implemented SQL Guardrails to restrict generated SQL to safe read-only queries and protect sensitive tables and fields.
- Designed Tool Calling with registry metadata, JSON Schema validation, RBAC, timeout, retry, trace and audit logging.
- Added async report generation with Celery, Redis, progress APIs, cancellation and report history.
- Implemented human-in-the-loop approval for email drafts and other sensitive actions.
- Created public-safe demo data, RAG documents, demo guide and GitHub presentation material.

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL + pgvector
- Queue: Redis + Celery
- Auth: JWT + RBAC
- AI application: RAG, SQL Agent, Tool Calling, Agent Planner, Mock Providers
- Deployment: Docker Compose

## Personal Responsibility Template

Responsible for end-to-end architecture and implementation, including backend API design, database schema design, Agent Planner orchestration, RAG pipeline, SQL safety controls, tool execution layer, async task workflow, frontend console integration, demo data preparation, documentation and public GitHub readiness.

## Interview Talking Points

- Why this project is more than a simple RAG chatbot.
- How SQL Agent can be useful while still being constrained by Guardrails.
- Why Mock providers make the project reproducible in interviews and CI.
- How traces help debug multi-step Agent behavior.
- How approval flow reduces risk for external actions.
- How the platform can evolve toward Langfuse, OpenTelemetry, eval datasets and production deployment.

## Quantified Expression Templates

- Implemented 6 Agent intents across RAG, SQL, Tool Calling, reports and approvals.
- Built 7 built-in tools with RBAC, schema validation, trace and audit logging.
- Created a public-safe demo dataset with 320 orders, 400 order items, 320 reviews and 153 after-sales records.
- Designed a local demo that runs without real API keys through Mock LLM and Embedding providers.

