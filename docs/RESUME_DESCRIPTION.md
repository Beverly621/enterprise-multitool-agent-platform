# Resume Description

## 中文简历短版

基于 FastAPI + Next.js + PostgreSQL/pgvector + Redis + Celery 设计并实现企业级多工具知识库 Agent 平台，支持 RAG 文档问答、SQL Agent 数据查询、Tool Calling、多步骤 Agent Planner、异步报告生成、RBAC 权限控制、SQL Guardrails、Human-in-the-loop 审批、Trace 与 Audit Log。系统内置 Mock LLM/Embedding Provider，在无真实 API Key 情况下也可本地完整运行 Demo。

## 中文简历长版

独立设计并实现企业级多工具知识库 Agent 平台，覆盖后端 API、数据库模型、Agent 编排、RAG 检索、SQL Agent、工具调用、异步任务、前端控制台、评测数据集、CI/CD 与公开展示文档。系统使用 FastAPI、SQLAlchemy、PostgreSQL/pgvector、Redis、Celery、Next.js 和 TypeScript 构建，支持基于文档的问答、结构化订单数据查询、多步骤报告生成、工具权限校验、审批流、Trace、Audit Log 与 Provider Metrics。项目默认使用 Mock LLM/Embedding Provider，可在无真实模型密钥的情况下完成本地 Demo 与 CI 验收；真实 Provider 通过环境变量接入，不在仓库中提交任何密钥。

## English Resume Short Version

Designed and implemented an enterprise-grade multi-tool AI Agent platform using FastAPI, Next.js, PostgreSQL/pgvector, Redis, and Celery. The platform supports RAG-based document QA, SQL Agent analytics, Tool Calling, multi-step Agent Planner workflows, asynchronous report generation, RBAC, SQL Guardrails, human-in-the-loop approvals, tracing, and audit logging. Built Mock LLM and Embedding providers to ensure the full demo can run locally without real API keys.

## English Resume Long Version

Designed and implemented an enterprise-grade multi-tool AI Agent platform covering backend APIs, database schema, Agent orchestration, RAG retrieval, SQL Agent analytics, Tool Calling, async task execution, frontend console integration, evaluation datasets, CI/CD, and public presentation documentation. The system uses FastAPI, SQLAlchemy, PostgreSQL/pgvector, Redis, Celery, Next.js, and TypeScript to support document QA, structured business-data analysis, multi-step report generation, tool permission checks, human approval workflows, traceability, audit logging, and provider metrics. Mock LLM and embedding providers make the demo reproducible without real API keys, while real providers can be configured through environment variables outside Git.

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

## Project Responsibilities

Responsible for end-to-end architecture and implementation, including backend API design, database schema design, Agent Planner orchestration, RAG pipeline, SQL safety controls, tool execution layer, async task workflow, frontend console integration, demo data preparation, documentation and public GitHub readiness.

## Role-Specific Resume Variants

### AI-Agent Developer

Implemented a multi-intent Agent runtime that routes user requests across RAG, SQL Agent, Tool Calling, approval-required actions, and multi-step report generation, with trace and audit records for each run.

### LLM Application Developer

Built a reproducible LLM application platform with provider abstraction, Mock provider fallback, prompt templates, RAG retrieval, SQL explanation, report generation, eval datasets, and public-safe demo workflows.

### Backend Developer

Designed FastAPI APIs, SQLAlchemy models, Alembic migrations, RBAC, JWT auth, SQL Guardrails, Celery tasks, Redis-backed async execution, Docker Compose, CI checks, and deployment templates.

### RAG Engineer

Implemented document parsing, chunking, embedding abstraction, pgvector storage, knowledge-base permissions, retrieval APIs, citation-aware answers, RAG eval cases, and demo policy documents.

### Platform Engineer

Added environment validation, Docker smoke tests, production Compose templates, GitHub Actions, public safety checks, observability metrics, regression runners, deployment docs, and release-facing project documentation.

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
- Added 80+ backend tests and frontend build validation in CI-oriented workflows.

Use these numbers only as project implementation scale. Do not present them as production traffic, customer impact, revenue, or live-user metrics.
