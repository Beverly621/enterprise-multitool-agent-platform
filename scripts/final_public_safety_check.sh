#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

status=0

ok() { printf '[OK] %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; status=1; }

tracked_files="$(git ls-files)"

if printf '%s\n' "$tracked_files" | grep -E '(^|/)\.env($|\.local$|\.[^.]+$)' | grep -vE '(^|/)\.env\.example$' >/dev/null; then
  fail "Tracked .env file found. Back it up outside Git, remove from tracking, and rotate any leaked secrets."
else
  ok "No tracked .env file except examples."
fi

if printf '%s\n' "$tracked_files" | grep -E '(^|/)(node_modules|\.next|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|coverage|htmlcov)(/|$)|(^|/)\.coverage$|\.log$|(^|/)\.DS_Store$' >/dev/null; then
  fail "Tracked generated cache/build/log artifact found."
else
  ok "No tracked generated cache/build/log artifacts."
fi

if find . \
  \( -path './.git' -o -path './frontend/node_modules' -o -path './node_modules' \) -prune \
  -o \( -name node_modules -o -name .next -o -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache -o -name coverage -o -name htmlcov -o -name .coverage -o -name '*.log' -o -name .DS_Store \) -print | grep . >/dev/null; then
  warn "Local generated files exist. Remove them before committing or packaging a release."
else
  ok "No local generated cache/build/log artifacts found."
fi

secret_patterns='(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY)'
if grep -RIE \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=.next \
  --exclude-dir=__pycache__ \
  --exclude-dir=.pytest_cache \
  --exclude='final_public_safety_check.sh' \
  "$secret_patterns" README.md RELEASE_NOTES.md docs data backend frontend scripts deploy .github >/dev/null 2>&1; then
  fail "High-confidence secret/key pattern found in public project files."
else
  ok "No high-confidence secret/key pattern found."
fi

if grep -RIE \
  --exclude='*.example' \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=.next \
  '(OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY).*=.+' README.md RELEASE_NOTES.md docs backend frontend scripts deploy >/dev/null 2>&1; then
  warn "Provider key assignment text exists outside example files. Confirm it is placeholder-only."
else
  ok "No provider key assignment found outside example files."
fi

if grep -RIE \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=.next \
  '(token|secret|password|private_key)' README.md RELEASE_NOTES.md docs data scripts deploy >/dev/null 2>&1; then
  warn "Generic sensitive words found. Review context before public release."
else
  ok "No generic sensitive words found in public docs/scripts."
fi

if [[ "$status" -ne 0 ]]; then
  printf '[NEXT] Fix FAIL items before publishing. For leaked secrets, rotate credentials and clean Git history.\n'
fi

exit "$status"
