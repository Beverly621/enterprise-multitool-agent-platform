#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

status=0

check_file() {
  if [[ -f "$1" ]]; then
    printf '[OK] %s\n' "$1"
  else
    printf '[FAIL] Missing %s\n' "$1"
    status=1
  fi
}

check_dir() {
  if [[ -d "$1" ]]; then
    printf '[OK] %s/\n' "$1"
  else
    printf '[FAIL] Missing %s/\n' "$1"
    status=1
  fi
}

check_dir backend
check_dir frontend
check_dir data
check_dir docs
check_dir scripts
check_dir deploy
check_dir .github/workflows

for file in \
  README.md \
  LICENSE \
  RELEASE_NOTES.md \
  .env.example \
  frontend/.env.example \
  .gitignore \
  docker-compose.yml \
  deploy/docker-compose.prod.yml \
  docs/PUBLIC_DATA_SOURCES.md \
  docs/DEMO_CASES.md \
  docs/DEMO_GUIDE.md \
  docs/RESUME_DESCRIPTION.md \
  docs/ARCHITECTURE_OVERVIEW.md \
  docs/DEMO_SCRIPT.md \
  docs/GITHUB_PUBLIC_CHECKLIST.md \
  docs/OBSERVABILITY_AND_EVAL.md \
  docs/EVAL_REPORT_TEMPLATE.md \
  docs/METRICS_DEFINITION.md \
  docs/REGRESSION_TEST_GUIDE.md \
  docs/DEPLOYMENT.md \
  docs/CI_CD.md \
  docs/PRODUCTION_CHECKLIST.md \
  docs/ENVIRONMENT_VARIABLES.md \
  docs/TROUBLESHOOTING_DEPLOYMENT.md \
  docs/INTERVIEW_QA.md \
  docs/ARCHITECTURE_EXPLAIN.md \
  docs/PROJECT_REVIEW.md \
  docs/TECHNICAL_HIGHLIGHTS.md \
  docs/CHALLENGES_AND_SOLUTIONS.md \
  docs/STAR_PROJECT_STORY.md \
  docs/PROJECT_FILE_MAP.md \
  docs/ROADMAP.md \
  docs/FINAL_PRESENTATION_GUIDE.md \
  docs/FINAL_CHECKLIST.md \
  docs/PROJECT_FINAL_REVIEW.md \
  docs/FINAL_ROADMAP.md \
  docs/FINAL_RELEASE_GUIDE.md \
  docs/THIRD_VALIDATION_PREP.md \
  scripts/check_public_safety.sh \
  scripts/pre_deploy_check.sh \
  scripts/docker_smoke_test.sh \
  scripts/final_public_safety_check.sh \
  scripts/final_repo_check.sh \
  scripts/final_smoke_test.sh \
  .github/workflows/backend-ci.yml \
  .github/workflows/frontend-ci.yml \
  .github/workflows/docker-build.yml \
  .github/workflows/public-safety.yml
do
  check_file "$file"
done

if grep -RIE --exclude='*.example' 'NEXT_PUBLIC_.*(OPENAI|ANTHROPIC|DEEPSEEK).*KEY' frontend >/dev/null 2>&1; then
  printf '[FAIL] Frontend exposes model provider key variable.\n'
  status=1
else
  printf '[OK] Frontend env does not expose model provider keys.\n'
fi

if [[ "$status" -eq 0 ]]; then
  printf 'FINAL CHECK PASSED\n'
else
  printf 'FINAL CHECK FAILED\n'
fi

exit "$status"
