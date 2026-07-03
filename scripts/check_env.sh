#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://agent:agent@postgres:5432/agent_platform}"
export REDIS_URL="${REDIS_URL:-redis://redis:6379/0}"
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-change-me-to-a-long-random-secret}"
export DEFAULT_LLM_PROVIDER="${DEFAULT_LLM_PROVIDER:-mock}"
export DEFAULT_EMBEDDING_PROVIDER="${DEFAULT_EMBEDDING_PROVIDER:-mock}"
export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8100}"
export NEXT_PUBLIC_APP_NAME="${NEXT_PUBLIC_APP_NAME:-Enterprise Multi-Tool Agent Platform}"

python3 "$ROOT_DIR/backend/scripts/check_env.py"
node "$ROOT_DIR/frontend/scripts/check_env.js"
