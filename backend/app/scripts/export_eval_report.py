from __future__ import annotations

import argparse
import json

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.metric import EvalResult, EvalRun


def main() -> None:
    parser = argparse.ArgumentParser(description="Export one eval run as JSON.")
    parser.add_argument("eval_run_id")
    args = parser.parse_args()
    with SessionLocal() as db:
        run = db.scalar(select(EvalRun).where(EvalRun.eval_run_id == args.eval_run_id))
        if run is None:
            raise SystemExit(f"Eval run not found: {args.eval_run_id}")
        results = db.scalars(select(EvalResult).where(EvalResult.eval_run_id == args.eval_run_id)).all()
    print(
        json.dumps(
            {
                "eval_run_id": run.eval_run_id,
                "case_type": run.case_type,
                "status": run.status,
                "total_cases": run.total_cases,
                "passed_cases": run.passed_cases,
                "failed_cases": run.failed_cases,
                "pass_rate": float(run.pass_rate or 0),
                "summary_json": run.summary_json,
                "results": [
                    {
                        "case_id": result.case_id,
                        "status": result.status,
                        "score": float(result.score or 0),
                        "error_message": result.error_message,
                    }
                    for result in results
                ],
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
