from __future__ import annotations

import argparse
import json

from app.core.database import SessionLocal
from app.services.regression_service import run_regression


def main() -> None:
    parser = argparse.ArgumentParser(description="Run core demo regression checks.")
    parser.add_argument("--no-db", action="store_true", help="Run without writing eval_runs/eval_results.")
    args = parser.parse_args()
    if args.no_db:
        result = run_regression(None)
    else:
        with SessionLocal() as db:
            result = run_regression(db)
    print(
        json.dumps(
            {
                "eval_run_id": result["eval_run_id"],
                "status": result["status"],
                "total": result["total_cases"],
                "passed": result["passed_cases"],
                "failed": result["failed_cases"],
                "pass_rate": result["pass_rate"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
