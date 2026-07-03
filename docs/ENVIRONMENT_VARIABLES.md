# Environment Variables

| Variable | Required | Default | Development | Production | Public |
| --- | --- | --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql+psycopg://agent:agent@postgres:5432/agent_platform` | Compose Postgres | Managed Postgres / private URL | No |
| `REDIS_URL` | Yes | `redis://redis:6379/0` | Compose Redis | Managed Redis / private URL | No |
| `JWT_SECRET_KEY` | Yes | placeholder only | Local placeholder acceptable | Strong secret required | No |
| `JWT_EXPIRE_MINUTES` | No | `1440` | Local sessions | Security policy dependent | Yes |
| `OPENAI_API_KEY` | Conditional | empty | Optional | Secret when OpenAI is enabled | No |
| `ANTHROPIC_API_KEY` | Conditional | empty | Optional | Secret when Anthropic is enabled | No |
| `DEEPSEEK_API_KEY` | Conditional | empty | Optional | Secret when DeepSeek is enabled | No |
| `DEFAULT_LLM_PROVIDER` | Yes | `mock` | `mock` recommended | `mock` or real provider | Yes |
| `DEFAULT_EMBEDDING_PROVIDER` | Yes | `mock` | `mock` recommended | `mock` or real provider | Yes |
| `VECTOR_DIMENSION` | No | `1536` | Match embedding provider | Match embedding provider | Yes |
| `CELERY_BROKER_URL` | No | `redis://redis:6379/1` | Compose Redis | Managed Redis | No |
| `CELERY_RESULT_BACKEND` | No | `redis://redis:6379/2` | Compose Redis | Managed Redis | No |
| `FRONTEND_ORIGIN` | Yes | `http://localhost:3100` | Local frontend | Production frontend URL | Yes |
| `DEMO_MODE` | No | `false` | `true` for demo | Usually `false` | Yes |
| `RUN_MIGRATIONS_ON_START` | No | `true` | `true` | Team policy dependent | Yes |
| `SEED_DEMO_ON_START` | No | `false` | Optional | Usually `false` | Yes |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | `http://localhost:8100` | Local backend URL | Public backend URL | Yes |
| `NEXT_PUBLIC_APP_NAME` | Yes | project name | Display name | Display name | Yes |

Mock provider mode allows all real provider keys to remain empty. Real provider mode requires the matching API key.
