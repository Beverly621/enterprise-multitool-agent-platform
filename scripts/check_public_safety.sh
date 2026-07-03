#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

status=0

ok() {
  printf '[OK] %s\n' "$1"
}

warn() {
  printf '[WARN] %s\n' "$1"
}

fail() {
  printf '[FAIL] %s\n' "$1"
  status=1
}

if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  tracked_files="$(git ls-files)"
else
  tracked_files="$(
    find . \
      \( -path './.git' -o -path './node_modules' -o -path './*/node_modules' \
      -o -path './__pycache__' -o -path './*/__pycache__' \
      -o -path './.pytest_cache' -o -path './*/.pytest_cache' \
      -o -path './.next' -o -path './*/.next' \) -prune \
      -o -type f -print | sed 's#^\./##'
  )"
fi

if printf '%s\n' "$tracked_files" | grep -E '(^|/)\.env($|\.local$|\.[^.]+$)' | grep -vE '(^|/)\.env\.example$' >/dev/null; then
  fail ".env file is tracked. Remove it from Git and keep only .env.example."
else
  ok "No tracked .env file found."
fi

if [[ -f .env || -f .env.local || -f backend/.env || -f frontend/.env.local ]]; then
  warn "Local env file exists. Keep it untracked and never commit real secrets."
else
  ok "No common local env file found in the working tree."
fi

if printf '%s\n' "$tracked_files" | grep -E '(^|/)(node_modules|__pycache__|\.pytest_cache|\.next)(/|$)' >/dev/null; then
  fail "Generated dependency/cache directory is tracked."
else
  ok "No tracked node_modules, __pycache__, .pytest_cache or .next directory."
fi

high_confidence_patterns='(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|ghp_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})'
scan_targets='README.md docs data backend/app frontend/app frontend/components scripts'
grep_excludes=(
  --exclude-dir=.git
  --exclude-dir=node_modules
  --exclude-dir=.next
  --exclude-dir=__pycache__
  --exclude-dir=.pytest_cache
)

if grep -RIE "${grep_excludes[@]}" "$high_confidence_patterns" $scan_targets >/dev/null 2>&1; then
  fail "High-confidence API key/token pattern found in public project files."
else
  ok "No high-confidence API key/token pattern found."
fi

if grep -RIE "${grep_excludes[@]}" '(OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY).*=.+' README.md docs backend frontend scripts --exclude='*.example' >/dev/null 2>&1; then
  warn "Provider key variable assignment text found. Confirm it is placeholder-only."
else
  ok "No provider API key assignment found outside example files."
fi

if grep -RIE "${grep_excludes[@]}" '(token|secret|password)' README.md docs data scripts >/dev/null 2>&1; then
  warn "Generic sensitive words found in docs/data/scripts. Review context before publishing."
else
  ok "No generic sensitive words found in docs/data/scripts."
fi

exit "$status"
