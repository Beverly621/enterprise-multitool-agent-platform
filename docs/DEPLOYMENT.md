# Deployment

This project supports local Docker Compose, production Docker Compose, and optional managed-platform deployments. The repository does not include real secrets. Configure secrets through `.env`, platform variables, or secret managers.

## Local Docker Compose

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
docker compose up -d --build
bash scripts/seed_demo_data.sh
```

Open:

- Frontend: `http://localhost:3100`
- Backend health: `http://localhost:8100/health`
- Backend docs: `http://localhost:8100/docs`

Local compose uses Mock providers by default and is safe to run without model API keys.

## Production Docker Compose

Use `deploy/docker-compose.prod.yml` as the production-oriented template:

```bash
docker compose -f deploy/docker-compose.prod.yml --env-file .env up -d --build
```

Production mode:

- Does not use frontend hot reload.
- Runs backend through `backend/scripts/prestart.sh`.
- Runs Alembic migrations when `RUN_MIGRATIONS_ON_START=true`.
- Does not seed demo data unless both `DEMO_MODE=true` and `SEED_DEMO_ON_START=true`.
- Uses Nginx as an optional reverse proxy with security headers.

## Required Services

- PostgreSQL with pgvector.
- Redis for cache, Celery broker, and task results.
- FastAPI backend.
- Celery worker.
- Next.js frontend.

## Environment Variables

See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md). Real provider keys must be configured through deployment platform secrets or a local untracked `.env`.

## Demo Mode vs Production Mode

`DEMO_MODE=true` enables demo-oriented behavior and permits demo seed flows. Production deployments should set:

```env
DEMO_MODE=false
SEED_DEMO_ON_START=false
ENVIRONMENT=prod
```

## Render

Use `deploy/render.yaml.example` as a starting point. Configure PostgreSQL and Redis as managed services, then set `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `FRONTEND_ORIGIN`, and provider settings in Render Environment Variables.

## Railway

Use Railway PostgreSQL and Redis plugins. See `deploy/railway.md`. Deploy backend and frontend separately, then set `NEXT_PUBLIC_API_BASE_URL` to the backend public URL.

## Fly.io

Use `deploy/fly.toml.example` as a backend starting point. Configure `fly secrets set` for `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, and any provider keys.

## Vercel

Deploy `frontend/` as the Vercel project root. Set:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend.example.com
NEXT_PUBLIC_APP_NAME=Enterprise Multi-Tool Agent Platform
```

Never set model API keys in `NEXT_PUBLIC_*`.

## Common Checks

```bash
bash scripts/check_public_safety.sh
bash scripts/check_env.sh
bash scripts/docker_smoke_test.sh
```

## Troubleshooting

See [TROUBLESHOOTING_DEPLOYMENT.md](TROUBLESHOOTING_DEPLOYMENT.md).
