#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_URL="${BACKEND_URL:-http://localhost:8100}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3100}"

cleanup() {
  docker compose logs backend --tail=80 || true
  docker compose logs celery_worker --tail=80 || true
}
trap cleanup ERR

echo "[INFO] Starting Docker smoke test with Mock providers."
docker compose down -v
docker compose up -d --build

echo "[INFO] Waiting for backend health..."
for attempt in {1..60}; do
  if curl -fsS "$BACKEND_URL/health" >/dev/null; then
    break
  fi
  if [[ "$attempt" == "60" ]]; then
    echo "[FAIL] Backend did not become healthy."
    exit 1
  fi
  sleep 2
done

curl -fsS "$BACKEND_URL/api/version" >/dev/null
bash scripts/seed_demo_data.sh

TOKEN="$(
  curl -fsS "$BACKEND_URL/api/auth/login" \
    -H 'Content-Type: application/json' \
    -d '{"email":"admin@example.com","password":"admin123"}' \
  | python3 -c 'import json,sys; payload=json.load(sys.stdin); print(payload.get("access_token") or payload["data"]["access_token"])'
)"

curl -fsS "$BACKEND_URL/api/agent/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"query":"你好，介绍一下这个平台","session_id":"docker-smoke"}' >/dev/null

curl -fsS -I "$FRONTEND_URL/" >/dev/null
echo "[OK] Docker smoke test passed."
