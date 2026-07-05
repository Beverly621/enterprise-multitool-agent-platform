from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.agent_run import AgentRun, AgentStep
from app.models.sql_query import SQLQueryLog
from app.models.tool import ToolCall
from app.scripts.eval_io import utc_timestamp, write_result


def main() -> None:
    payload = _load_stats()
    write_result("stats.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _load_stats() -> dict[str, Any]:
    db_error: str | None = None
    try:
        with SessionLocal() as db:
            total_agent_runs = db.scalar(select(func.count(AgentRun.id))) or 0
            total_agent_steps = db.scalar(select(func.count(AgentStep.id))) or 0
            total_tool_calls = db.scalar(select(func.count(ToolCall.id))) or 0
            total_sql_queries = db.scalar(select(func.count(SQLQueryLog.id))) or 0
            total_guardrails_blocks = (
                db.scalar(select(func.count(SQLQueryLog.id)).where(SQLQueryLog.safe.is_(False))) or 0
            )
            total_failed_runs = (
                db.scalar(
                    select(func.count(AgentRun.id)).where(
                        func.lower(AgentRun.status).in_(("failed", "error"))
                    )
                )
                or 0
            )
            last_run_at = db.scalar(select(func.max(AgentRun.created_at)))
    except Exception as exc:  # pragma: no cover - exercised when local DB is unavailable.
        db_error = exc.__class__.__name__
        total_agent_runs = 0
        total_agent_steps = 0
        total_tool_calls = 0
        total_sql_queries = 0
        total_guardrails_blocks = 0
        total_failed_runs = 0
        last_run_at = None

    payload = {
        "total_agent_runs": total_agent_runs,
        "total_agent_steps": total_agent_steps,
        "total_tool_calls": total_tool_calls,
        "total_sql_queries": total_sql_queries,
        "total_guardrails_blocks": total_guardrails_blocks,
        "total_failed_runs": total_failed_runs,
        "avg_steps_per_run": round(total_agent_steps / total_agent_runs, 4) if total_agent_runs else 0,
        "last_run_at": last_run_at.isoformat() if last_run_at else None,
        "timestamp": utc_timestamp(),
        "result_file": "backend/app/eval_results/stats.json",
        "db_available": db_error is None,
    }
    if db_error:
        payload["db_error_type"] = db_error
    return payload


if __name__ == "__main__":
    main()
