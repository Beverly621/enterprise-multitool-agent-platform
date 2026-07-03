# CI/CD

GitHub Actions workflows live in `.github/workflows/`.

## backend-ci.yml

Runs on push to `main` and pull requests.

Steps:

- Checkout.
- Setup Python 3.12.
- Start PostgreSQL with pgvector and Redis services.
- Install backend dependencies.
- Validate backend environment.
- Run `python -m pytest app/tests`.

The workflow uses Mock providers and does not require real model API keys.

## frontend-ci.yml

Steps:

- Checkout.
- Setup Node.js 22.
- Run `npm ci`.
- Validate frontend environment.
- Run `npm run lint`.
- Run `npm run build`.

## docker-build.yml

Builds the development compose images and production compose images. It does not push images.

## public-safety.yml

Runs:

```bash
bash scripts/check_public_safety.sh
```

It checks tracked env files, generated directories, logs, and high-confidence secret patterns.

## Local CI Reproduction

```bash
cd backend
python -m pytest app/tests

cd ../frontend
npm ci
npm run lint
npm run build

cd ..
bash scripts/check_public_safety.sh
docker compose build
```

## Secrets

CI does not need real provider keys. If a deployment workflow later needs secrets, use GitHub Secrets such as:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `DEEPSEEK_API_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`

Never print full environment dumps or upload `.env` files as artifacts.

## Failure Triage

- Backend test failures: check PostgreSQL/Redis service health and migrations.
- Frontend build failures: check `NEXT_PUBLIC_API_BASE_URL` and TypeScript errors.
- Docker build failures: check `.dockerignore`, lockfiles, and required compose variables.
- Public safety failures: remove tracked generated files or sensitive content before retrying.
