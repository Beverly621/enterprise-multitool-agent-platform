#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_URL="${BACKEND_URL:-http://localhost:8100}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3100}"

cleanup() {
  exit_code=$?
  if [[ "$exit_code" -ne 0 ]]; then
    docker compose logs backend --tail=120 || true
    docker compose logs celery_worker --tail=120 || true
  fi
  docker compose down -v >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[INFO] Final smoke test: cold-starting Docker Compose."
docker compose down -v
docker compose up -d --build

echo "[INFO] Waiting for backend health..."
for attempt in {1..90}; do
  if curl -fsS "$BACKEND_URL/health" >/dev/null; then
    break
  fi
  if [[ "$attempt" == "90" ]]; then
    echo "[FAIL] Backend did not become healthy."
    exit 1
  fi
  sleep 2
done

curl -fsS "$BACKEND_URL/api/version" >/dev/null

echo "[INFO] Seeding demo data."
bash scripts/seed_demo_data.sh

echo "[INFO] Logging in as admin demo user."
TOKEN="$(
  curl -fsS "$BACKEND_URL/api/auth/login" \
    -H 'Content-Type: application/json' \
    -d '{"email":"admin@example.com","password":"admin123"}' \
  | python3 -c 'import json,sys; payload=json.load(sys.stdin); print(payload.get("access_token") or payload["data"]["access_token"])'
)"

auth_header=(-H "Authorization: Bearer $TOKEN")

echo "[INFO] Running general Agent chat."
curl -fsS "$BACKEND_URL/api/agent/chat" \
  "${auth_header[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"query":"你好，介绍一下这个平台","session_id":"final-smoke-general"}' >/dev/null

echo "[INFO] Running multi-step Agent report prompt."
REPORT_RESPONSE="$(
  curl -fsS "$BACKEND_URL/api/agent/chat" \
    "${auth_header[@]}" \
    -H 'Content-Type: application/json' \
    -d '{"query":"结合最近 30 天订单异常数据和售后知识库生成一份分析报告。","session_id":"final-smoke-report"}'
)"

RUN_ID="$(printf '%s' "$REPORT_RESPONSE" | python3 -c 'import json,sys; payload=json.load(sys.stdin); data=payload.get("data", payload); print(data.get("run_id", ""))')"
if [[ -z "$RUN_ID" ]]; then
  echo "[FAIL] Multi-step Agent response did not include run_id."
  exit 1
fi

curl -fsS "$BACKEND_URL/api/reports" "${auth_header[@]}" >/dev/null
curl -fsS "$BACKEND_URL/api/runs" "${auth_header[@]}" >/dev/null
curl -fsS "$BACKEND_URL/api/runs/$RUN_ID/traces" "${auth_header[@]}" >/dev/null
curl -fsS -I "$FRONTEND_URL/" >/dev/null

echo "[OK] Final smoke test passed."
