#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESET_FLAG=""

if [[ "${1:-}" == "--reset" ]]; then
  RESET_FLAG="--reset"
fi

cd "$ROOT_DIR"

if command -v docker >/dev/null 2>&1 && docker compose ps --services --filter status=running | grep -qx "backend"; then
  docker compose exec backend python -m app.seed.seed_all ${RESET_FLAG}
else
  cd "$ROOT_DIR/backend"
  python -m app.seed.seed_all ${RESET_FLAG}
fi

cat <<'EOF'

Demo seed completed.

Demo accounts:
- admin@example.com / admin123
- developer@example.com / dev123
- user@example.com / user123
- guest@example.com / guest123

Demo docs:
- data/demo_docs/sample_company_policy.md
- data/demo_docs/sample_after_sales_policy.md
- data/demo_docs/sample_return_policy.md
- data/demo_docs/sample_order_abnormal_handbook.md

Recommended question:
结合最近 30 天订单异常数据和售后知识库生成一份分析报告。
EOF
