#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

run() {
  printf '\n==> %s\n' "$*"
  "$@"
}

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git ls-files | grep -E '(^|/)\.env($|\.local$|\.[^.]+$)' | grep -vE '(^|/)\.env\.example$' >/dev/null; then
    echo "[FAIL] A non-example .env file is tracked."
    exit 1
  fi
  if [[ -n "$(git status --short)" ]]; then
    echo "[WARN] Working tree has local changes. Confirm they are intended before deployment."
    git status --short
  fi
fi

run bash scripts/check_public_safety.sh
run bash scripts/check_env.sh
run bash -c "cd backend && python3 -m pytest app/tests"
run npm --prefix frontend install
run npm --prefix frontend run lint
run npm --prefix frontend run build
run docker compose build

if ! grep -q "Quick Start" README.md || ! grep -q "Deployment" README.md; then
  echo "[FAIL] README must include Quick Start and Deployment sections."
  exit 1
fi

echo "[OK] Pre-deploy check completed."
