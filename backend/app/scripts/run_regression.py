from __future__ import annotations

import argparse
import json
from typing import Any

from app.core.database import SessionLocal
from app.scripts.eval_io import summarize_eval_result, utc_timestamp, write_result
from app.services.regression_service import run_regression


def main() -> None:
    parser = argparse.ArgumentParser(description="Run core demo regression checks.")
    parser.add_argument("--no-db", action="store_true", help="Run without writing eval_runs/eval_results.")
    args = parser.parse_args()
    payload = _run(args.no_db)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _run(no_db: bool) -> dict[str, Any]:
    db_error: str | None = None
    if no_db:
        result = run_regression(None)
    else:
        try:
            with SessionLocal() as db:
                result = run_regression(db)
        except Exception as exc:  # pragma: no cover - exercised when local DB is unavailable.
            db_error = exc.__class__.__name__
            result = run_regression(None)
    payload = summarize_eval_result(result, timestamp=utc_timestamp())
    payload["result_file"] = "backend/app/eval_results/regression.json"
    payload["db_write"] = "skipped" if no_db or db_error else "completed"
    if db_error:
        payload["db_error_type"] = db_error
    write_result("regression.json", payload)
    return payload


if __name__ == "__main__":
    main()
