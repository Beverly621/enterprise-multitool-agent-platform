from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


RESULT_DIR = Path(__file__).resolve().parents[1] / "eval_results"


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def write_result(filename: str, payload: dict[str, Any]) -> Path:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULT_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path


def summarize_eval_result(result: dict[str, Any], *, timestamp: str | None = None) -> dict[str, Any]:
    failed_case_ids = [
        item["case_id"]
        for item in result.get("results", [])
        if item.get("status") != "PASSED"
    ]
    summary = {
        "eval_run_id": result.get("eval_run_id"),
        "case_type": result.get("case_type"),
        "status": result.get("status"),
        "total_cases": result.get("total_cases", 0),
        "passed_cases": result.get("passed_cases", 0),
        "failed_cases": result.get("failed_cases", 0),
        "pass_rate": result.get("pass_rate", 0),
        "failed_case_ids": failed_case_ids,
        "timestamp": timestamp or utc_timestamp(),
        "summary": result.get("summary", {}),
    }
    if result.get("case_type") == "SQL_GUARDRAILS":
        summary.update(_sql_guardrails_block_summary(result))
    return summary


def aggregate_eval_summaries(summaries: list[dict[str, Any]], *, timestamp: str | None = None) -> dict[str, Any]:
    total_cases = sum(int(item.get("total_cases", 0)) for item in summaries)
    passed_cases = sum(int(item.get("passed_cases", 0)) for item in summaries)
    failed_cases = total_cases - passed_cases
    return {
        "case_type": "ALL",
        "status": "PASSED" if failed_cases == 0 else "FAILED",
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "pass_rate": round(passed_cases / total_cases, 4) if total_cases else 0,
        "failed_case_ids": [
            case_id
            for item in summaries
            for case_id in item.get("failed_case_ids", [])
        ],
        "timestamp": timestamp or utc_timestamp(),
        "suites": summaries,
    }


def _sql_guardrails_block_summary(result: dict[str, Any]) -> dict[str, Any]:
    unsafe_total = 0
    unsafe_blocked = 0
    for item in result.get("results", []):
        expected = item.get("expected_json") or {}
        actual = item.get("actual_json") or {}
        if expected.get("expected_safe") is False:
            unsafe_total += 1
            if actual.get("safe") is False:
                unsafe_blocked += 1
    return {
        "total_unsafe_sql_cases": unsafe_total,
        "blocked_unsafe_sql_cases": unsafe_blocked,
        "unsafe_sql_block_rate": round(unsafe_blocked / unsafe_total, 4) if unsafe_total else 0,
    }
