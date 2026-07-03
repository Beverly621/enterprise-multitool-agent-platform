# Project Review

## Project Background

The project was built to demonstrate an enterprise-grade Agent application beyond a single RAG chatbot. It uses simulated business data and public-safe documents to show how an internal AI platform might combine knowledge retrieval, structured analytics, tools, approvals and observability.

## Why Build It

Many portfolio projects stop at prompt calls or basic document QA. This project focuses on engineering depth: safety, async execution, RBAC, traceability, evals, CI/CD and reproducible local demos without private credentials.

## Requirement Breakdown

- RAG for policy and after-sales documents.
- SQL Agent for demo order analytics.
- Tool Calling for controlled actions.
- Agent Planner for multi-intent orchestration.
- Async reports for long-running work.
- Frontend console for real API workflows.
- Trace, audit, metrics and eval for assurance.
- Docker and CI/CD for reproducible validation.

## Technical Choices

FastAPI provides typed APIs and a clear service structure. Next.js and TypeScript provide a structured console. PostgreSQL with pgvector keeps relational and vector data together for the demo. Redis and Celery support long tasks. Mock providers keep the project public-safe and repeatable.

## Stage Progress

The project progressed from backend foundation and RAG to SQL Agent, Tool Calling, Agent Planner, async reports, frontend console, demo data, observability/eval, deployment configuration and final presentation materials.

## Core Modules

Core modules include `backend/app/api`, `backend/app/services`, `backend/app/agent`, `backend/app/tasks`, `backend/app/models`, `frontend/app`, `docs`, `scripts`, `deploy` and `.github/workflows`.

## Problems Encountered

The hardest parts were making multiple Agent capabilities feel unified, ensuring SQL safety, keeping the public repo free of secrets, and making the demo deterministic enough for interviews and CI.

## Solutions

The project uses explicit planner nodes, SQL Guardrails, Mock providers, public-safe seed data, trace/audit tables, docs-based demo flows, Docker smoke tests, pre-deploy checks and public safety scanning.

## Current Limitations

The project is not claiming a live production deployment. Production use would still require real provider secrets, stronger tenant isolation, backup/restore, SSO, runtime monitoring, incident playbooks and operational hardening.

## Future Optimization

Planned improvements include Langfuse/OpenTelemetry export, more document formats, Playwright E2E tests, richer dashboards, tenant isolation, enterprise SSO, workflow editing and plugin packaging.

## Personal Takeaways

The project strengthened the link between LLM product features and backend engineering discipline: a useful Agent platform needs not only prompts, but permissions, traceability, testing, deployment configuration and honest documentation.
