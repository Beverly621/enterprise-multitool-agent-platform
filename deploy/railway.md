# Railway Deployment Notes

Use Railway PostgreSQL and Redis plugins, then deploy the backend and frontend as separate services.

Required backend variables: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `FRONTEND_ORIGIN`, `DEFAULT_LLM_PROVIDER`, `DEFAULT_EMBEDDING_PROVIDER`.

Use Mock providers by default. Configure provider API keys only through Railway Variables when switching to real providers.
