#!/usr/bin/env sh
set -eu

python /app/scripts/check_env.py

python - <<'PY'
import os
import time

import psycopg
from redis import Redis

database_url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
redis_url = os.environ["REDIS_URL"]

for attempt in range(1, 31):
    try:
        with psycopg.connect(database_url, connect_timeout=3) as conn:
            conn.execute("select 1")
        break
    except Exception as exc:
        if attempt == 30:
            raise
        print(f"Waiting for database ({attempt}/30): {exc.__class__.__name__}")
        time.sleep(2)

for attempt in range(1, 31):
    try:
        Redis.from_url(redis_url).ping()
        break
    except Exception as exc:
        if attempt == 30:
            raise
        print(f"Waiting for Redis ({attempt}/30): {exc.__class__.__name__}")
        time.sleep(2)
PY

if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
  alembic -c alembic.ini upgrade head
fi

if [ "${DEMO_MODE:-false}" = "true" ] && [ "${SEED_DEMO_ON_START:-false}" = "true" ]; then
  python -m app.seed.seed_all
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
