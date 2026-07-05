from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from typing import Any

from app.core.database import SessionLocal
from app.scripts.eval_io import aggregate_eval_summaries, summarize_eval_result, utc_timestamp, write_result
from app.services.agent_eval_service import run_agent_eval
from app.services.rag_eval_service import run_rag_eval
from app.services.sql_guardrails_eval_service import run_sql_guardrails_eval
from app.services.tool_eval_service import run_tool_eval

Runner = Callable[[Any], dict[str, Any]]

RUNNERS: dict[str, tuple[Runner, str]] = {
    "rag": (run_rag_eval, "rag_eval.json"),
    "sql-guardrails": (run_sql_guardrails_eval, "sql_guardrails_eval.json"),
    "tool": (run_tool_eval, "tool_eval.json"),
    "agent": (run_agent_eval, "agent_eval.json"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run observability eval suites.")
    parser.add_argument("--type", choices=["rag", "sql-guardrails", "tool", "agent", "all"], required=True)
    parser.add_argument("--no-db", action="store_true", help="Run without writing eval_runs/eval_results.")
    args = parser.parse_args()

    timestamp = utc_timestamp()
    if args.type == "all":
        summaries = [_run_suite(eval_type, args.no_db, timestamp) for eval_type in RUNNERS]
        payload = aggregate_eval_summaries(summaries, timestamp=timestamp)
        write_result("all_eval.json", payload)
    else:
        payload = _run_suite(args.type, args.no_db, timestamp)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _run_suite(eval_type: str, no_db: bool, timestamp: str) -> dict[str, Any]:
    runner, filename = RUNNERS[eval_type]
    db_error: str | None = None
    if no_db:
        result = runner(None)
    else:
        try:
            with SessionLocal() as db:
                result = runner(db)
        except Exception as exc:  # pragma: no cover - exercised when local DB is unavailable.
            db_error = exc.__class__.__name__
            result = runner(None)
    payload = summarize_eval_result(result, timestamp=timestamp)
    payload["result_file"] = f"backend/app/eval_results/{filename}"
    payload["db_write"] = "skipped" if no_db or db_error else "completed"
    if db_error:
        payload["db_error_type"] = db_error
    write_result(filename, payload)
    return payload


if __name__ == "__main__":
    main()
