# Deployment Troubleshooting

## Docker Build Fails

Run `docker compose build --no-cache` and check whether dependency lockfiles are copied correctly. Verify `.dockerignore` is not excluding required files.

## Backend Cannot Connect to Postgres

Check `DATABASE_URL`, container DNS names, PostgreSQL health status, and credentials. For local compose, the host should be `postgres`.

## Backend Cannot Connect to Redis

Check `REDIS_URL` and Redis health. For local compose, the host should be `redis`.

## Alembic Migration Fails

Run:

```bash
cd backend
alembic -c alembic.ini current
alembic -c alembic.ini upgrade head
```

Confirm the database user can create tables and extensions.

## pgvector Extension Missing

Use the `pgvector/pgvector:pg16` image or install pgvector on the managed PostgreSQL service.

## Celery Worker Fails

Check `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, Redis availability, and imports in `app.tasks.celery_app`.

## Frontend Build Fails

Run `npm ci`, `npm run lint`, and `npm run build` inside `frontend/`. Confirm `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_APP_NAME` exist.

## CORS Error

Set `FRONTEND_ORIGIN` to the exact frontend URL. Do not use `*` with credentials in production.

## Login Returns 401

Confirm demo users were seeded or production users exist. Check `JWT_SECRET_KEY` consistency across backend replicas.

## Mock Provider Does Not Work

Set:

```env
DEFAULT_LLM_PROVIDER=mock
DEFAULT_EMBEDDING_PROVIDER=mock
```

## Real Provider API Key Missing

Set the matching secret for the selected provider. For example, `DEFAULT_LLM_PROVIDER=openai` requires `OPENAI_API_KEY`.

## Vercel Frontend Cannot Reach Backend

Check `NEXT_PUBLIC_API_BASE_URL`, backend public URL, HTTPS, and backend CORS `FRONTEND_ORIGIN`.

## Render Backend Cold Start

Check health endpoint timing, managed database availability, and migration duration.

## Railway Database URL Error

Use Railway's internal database URL for backend service-to-database traffic. Confirm the URL scheme is compatible with `psycopg`.
