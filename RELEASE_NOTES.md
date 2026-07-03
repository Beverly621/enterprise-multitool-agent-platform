# Release Notes

## v1.0.0-demo

Release date: To be filled after final `03-test.md` validation.

## Overview

`v1.0.0-demo` is the portfolio/demo release candidate for Enterprise Multi-Tool Agent Platform. It packages the completed engineering work from phases 1 through 12 and prepares the repository for public GitHub review, final validation and optional release tagging.

## Core Features

- RAG document Q&A with parsing, chunking, embeddings, pgvector retrieval and citations.
- SQL Agent analytics with schema reading, SQL Guardrails and safe read-only execution.
- Tool Calling with registry metadata, schema validation, RBAC, timeout/retry policies, trace and audit.
- Agent Planner for general chat, RAG, SQL, tools, approvals and multi-step reports.
- Async Agent tasks and report generation with Celery, Redis, progress APIs and report history.
- Human-in-the-loop approval for sensitive actions such as email draft generation.
- Frontend console for Dashboard, Knowledge Base, Agent Chat, SQL Agent, Tools, Approvals, Runs, Tasks, Reports, Audit and Admin Users.
- Metrics, provider-call tracking, eval datasets and regression runners.
- Docker Compose, production Compose template, CI workflows and public safety checks.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic.
- Frontend: Next.js, React, TypeScript, Tailwind CSS.
- Data: PostgreSQL 16, pgvector, Redis.
- Async: Celery.
- Auth and safety: JWT, RBAC, SQL Guardrails, human approval.
- Demo providers: Mock LLM and Mock Embedding providers by default.

## Demo Capability

The project can run locally without real model API keys. Demo data is simulated or self-written public-safe material under `data/demo_docs/` and `data/demo_orders/`.

## Security Design

- Real `.env` files and secrets are not committed.
- Model provider keys are optional and configured outside Git.
- Frontend public variables do not include model API keys.
- SQL Agent is constrained by Guardrails.
- Sensitive tool actions require approval.
- Trace, audit and public safety scripts support review before publishing.

## Known Limits

- This release is demo-ready and production-oriented, but it does not claim a live production deployment.
- Demo data is simulated and should not be represented as real enterprise data.
- Mock providers are intended for reproducible local demos and CI, not production model quality.
- Production rollout would require tenant isolation, SSO, monitoring, backups, rate limiting and operational runbooks.

## Next Steps

- Run final `03-test.md` from zero clone.
- Capture real screenshots from the final demo run.
- Add Langfuse or OpenTelemetry trace export.
- Add Playwright E2E tests.
- Strengthen multi-tenant isolation and enterprise auth.
