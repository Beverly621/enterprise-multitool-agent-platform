# Demo Cases

## Stage 1

1. Start the stack with `docker compose up -d`.
2. Seed demo users with `docker compose exec backend python -m app.seed.seed_all`.
3. Open Swagger at http://localhost:8100/docs.
4. Log in as `admin@example.com` with `admin123`.
5. Call `/api/auth/me`, `/api/users` and `/api/roles` with the returned bearer token.
