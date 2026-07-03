from __future__ import annotations

import argparse
import json

from app.core.database import SessionLocal
from app.services.agent_eval_service import run_agent_eval
from app.services.rag_eval_service import run_rag_eval
from app.services.sql_guardrails_eval_service import run_sql_guardrails_eval
from app.services.tool_eval_service import run_tool_eval


def main() -> None:
    parser = argparse.ArgumentParser(description="Run observability eval suites.")
    parser.add_argument("--type", choices=["rag", "sql-guardrails", "tool", "agent"], required=True)
    parser.add_argument("--no-db", action="store_true", help="Run without writing eval_runs/eval_results.")
    args = parser.parse_args()

    runner = {
        "rag": run_rag_eval,
        "sql-guardrails": run_sql_guardrails_eval,
        "tool": run_tool_eval,
        "agent": run_agent_eval,
    }[args.type]

    if args.no_db:
        result = runner(None)
    else:
        with SessionLocal() as db:
            result = runner(db)
    print(json.dumps(_summary(result), ensure_ascii=False, indent=2))


def _summary(result: dict) -> dict:
    return {
        "eval_run_id": result["eval_run_id"],
        "case_type": result["case_type"],
        "status": result["status"],
        "total": result["total_cases"],
        "passed": result["passed_cases"],
        "failed": result["failed_cases"],
        "pass_rate": result["pass_rate"],
        "summary": result.get("summary", {}),
    }


if __name__ == "__main__":
    main()
