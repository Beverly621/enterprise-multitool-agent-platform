from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.services.base_eval_service import EvalCaseResult, persist_eval_run
from app.services.eval_case_loader import load_eval_cases
from app.services.sql_guardrails import validate_sql
from app.tools import get_builtin_tools


def run_tool_eval(db: Session | None = None, created_by: int | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    tools = get_builtin_tools()
    results: list[EvalCaseResult] = []
    for case in load_eval_cases("tool"):
        case_started = time.perf_counter()
        tool_name = case["tool_name"]
        expected = case["expected"]
        tool = tools.get(tool_name)
        actual: dict[str, Any] = {"tool_exists": tool is not None}
        if tool is not None:
            actual.update(
                {
                    "permission_level": tool.metadata.permission_level,
                    "requires_approval": tool.metadata.require_approval,
                }
            )
        if tool_name == "execute_safe_sql" and case.get("args", {}).get("sql"):
            guardrail = validate_sql(case["args"]["sql"])
            actual["guardrail_safe"] = guardrail.safe
        passed = all(actual.get(key) == value for key, value in expected.items())
        results.append(
            EvalCaseResult(
                case_id=case["case_id"],
                status="PASSED" if passed else "FAILED",
                score=1.0 if passed else 0.0,
                input_json={"tool_name": tool_name, "args": case.get("args", {})},
                expected_json=expected,
                actual_json=actual,
                error_message=None if passed else "Tool metadata expectation mismatch",
                duration_ms=int((time.perf_counter() - case_started) * 1000),
            )
        )
    return persist_eval_run(db, "TOOL_CALL", results, {"mode": "metadata_and_guardrail"}, created_by, started)
