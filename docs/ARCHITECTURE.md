# Architecture

The platform is organized as a layered FastAPI backend and a Next.js admin/demo frontend.

## Runtime Components

- `backend`: FastAPI API service with JWT auth, RBAC, provider abstraction and database access.
- `frontend`: Next.js console for platform status and later admin workflows.
- `postgres`: PostgreSQL 16 with pgvector enabled for future vector search.
- `redis`: session, task state and Celery broker/result backend.
- `celery_worker`: asynchronous worker for document, embedding and report tasks.
- `celery_beat`: optional scheduled task runner under the `beat` profile.

## Backend Layers

- `api`: HTTP routers and request/response boundaries.
- `services`: business logic and provider abstractions.
- `models`: SQLAlchemy ORM models.
- `tasks`: Celery application and async task entrypoints.
- `core`: settings, database, Redis, security and logging.
- `agent`: reserved for LangGraph planner/runtime implementation in later phases.

