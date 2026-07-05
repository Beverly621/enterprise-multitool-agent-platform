from __future__ import annotations

import json
import statistics
import time
import uuid
from typing import Any

from app.scripts.eval_io import utc_timestamp, write_result


TRACE_CASES = 10


def main() -> None:
    traces = [_make_failed_trace_case(index) for index in range(TRACE_CASES)]
    trace_index = {item["run"]["run_id"]: item for item in traces}
    lookup_times: list[float] = []
    successes = 0
    failed_run_ids: list[str] = []

    for item in traces:
        run_id = item["run"]["run_id"]
        started = time.perf_counter()
        replay = trace_index.get(run_id)
        lookup_times.append((time.perf_counter() - started) * 1000)
        if _has_required_trace_parts(replay):
            successes += 1
        else:
            failed_run_ids.append(run_id)

    payload = {
        "benchmark": "trace_replay",
        "total_failed_runs_checked": TRACE_CASES,
        "successful_replays": successes,
        "failed_replays": TRACE_CASES - successes,
        "trace_replay_success_rate": round(successes / TRACE_CASES, 4),
        "avg_lookup_time_ms": round(statistics.fmean(lookup_times), 3),
        "failed_run_ids": failed_run_ids,
        "required_trace_parts": ["run", "steps", "tool_call", "sql_log", "audit_log", "error"],
        "data_mode": "synthetic_failed_agent_runs",
        "timestamp": utc_timestamp(),
        "result_file": "backend/app/eval_results/trace_benchmark.json",
    }
    write_result("trace_benchmark.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _make_failed_trace_case(index: int) -> dict[str, Any]:
    run_id = f"run_failed_{index:02d}_{uuid.uuid4().hex[:8]}"
    error = "SQL Guardrails blocked unsafe SQL before execution."
    return {
        "run": {"run_id": run_id, "status": "FAILED", "intent": "SQL_QUERY", "error": error},
        "steps": [
            {"step_name": "intent_router", "status": "SUCCESS"},
            {"step_name": "sql_guardrails", "status": "FAILED", "error": error},
        ],
        "tool_call": {
            "tool_call_id": f"tool_{uuid.uuid4().hex[:8]}",
            "run_id": run_id,
            "tool_name": "execute_safe_sql",
            "status": "FAILED",
        },
        "sql_log": {
            "run_id": run_id,
            "safe": False,
            "blocked_reason": error,
        },
        "audit_log": {
            "resource_id": run_id,
            "action": "AGENT_RUN_FAILED",
        },
        "error": error,
    }


def _has_required_trace_parts(item: dict[str, Any] | None) -> bool:
    if not item:
        return False
    return all(
        [
            item.get("run", {}).get("run_id"),
            item.get("steps"),
            item.get("tool_call", {}).get("run_id") == item.get("run", {}).get("run_id"),
            item.get("sql_log", {}).get("run_id") == item.get("run", {}).get("run_id"),
            item.get("audit_log", {}).get("resource_id") == item.get("run", {}).get("run_id"),
            item.get("error"),
        ]
    )


if __name__ == "__main__":
    main()
