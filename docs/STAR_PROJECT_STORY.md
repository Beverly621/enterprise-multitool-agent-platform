# STAR Project Story

## 30-Second Version

- Situation: I wanted a portfolio project that showed more than a basic RAG chatbot.
- Task: Build a reproducible enterprise-style Agent platform with RAG, SQL Agent, tools, approvals, async reports, traceability and CI/CD.
- Action: I implemented the FastAPI backend, Next.js console, PostgreSQL/pgvector data layer, Celery tasks, SQL Guardrails, Mock providers, demo data, evals and deployment checks.
- Result: The final project can run locally without real API keys, demonstrate multiple Agent workflows, and provide interview-ready docs, traces, tests and safety checks.

## 2-Minute Version

- Situation: Many LLM demos are hard to evaluate because they either depend on private credentials or only show a single chat path.
- Task: I designed a project that could be publicly reviewed and still show realistic enterprise concerns: permissions, SQL safety, tool risk, long-running jobs and observability.
- Action: I split the system into a Next.js console, FastAPI APIs, explicit Agent planner nodes, RAG services, SQL Agent services, tool execution, approval services, Celery tasks, trace/audit logging, metrics and eval runners. I used simulated demo orders and self-written policy documents, then added Docker Compose, CI workflows and public safety checks.
- Result: The project now supports a full demo path from login to RAG, SQL analytics, multi-step reports, approvals, run traces, reports and audit logs. It is suitable for GitHub review, resume discussion and interview walkthroughs without claiming live production usage.

## 5-Minute Version

- Situation: I wanted to demonstrate LLM application engineering in a way that covers real backend concerns, not only prompt design. Enterprise Agent systems usually need access control, safe data access, traceability, async execution, evaluation and deployment hygiene.
- Task: The goal was to build an end-to-end multi-tool Agent platform that could combine unstructured policy documents, structured order data and tool actions, while remaining public-safe and reproducible for interviews.
- Action: I implemented the backend with FastAPI, SQLAlchemy, PostgreSQL/pgvector, Redis and Celery. I built document parsing, chunking, embeddings and vector retrieval for RAG; schema reading, SQL Guardrails and safe execution for SQL Agent; a tool registry with validation, permissions and approval requirements; and an Agent Planner that routes requests across chat, RAG, SQL, tools and reports. On the frontend I added pages for dashboard, KB, Agent Chat, SQL Agent, tools, approvals, runs, tasks, reports and audit. I also added Mock providers, demo data, eval datasets, regression runners, Docker Compose, CI/CD, environment checks, public safety scans and presentation docs.
- Result: The project can be run locally with Docker and demo seed data, inspected through real frontend pages, and validated with backend tests, frontend build, smoke tests and safety checks. It is honest about being a demo-ready portfolio project, while still showing the engineering patterns expected in a production-oriented Agent platform.
