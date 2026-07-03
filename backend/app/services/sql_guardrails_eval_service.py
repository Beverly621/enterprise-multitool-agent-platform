from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.services.base_eval_service import EvalCaseResult, persist_eval_run
from app.services.eval_case_loader import load_eval_cases
from app.services.sql_guardrails import validate_sql


def run_sql_guardrails_eval(db: Session | None = None, created_by: int | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    results: list[EvalCaseResult] = []
    false_negative = 0
    false_positive = 0
    for case in load_eval_cases("sql-guardrails"):
        case_started = time.perf_counter()
        result = validate_sql(case["sql"])
        expected_safe = bool(case["expected_safe"])
        if result.safe and not expected_safe:
            false_negative += 1
        if not result.safe and expected_safe:
            false_positive += 1
        reason_ok = True
        if case.get("expected_reason_contains"):
            reason_ok = case["expected_reason_contains"].lower() in (result.reason or "").lower()
        passed = result.safe == expected_safe and reason_ok
        results.append(
            EvalCaseResult(
                case_id=case["case_id"],
                status="PASSED" if passed else "FAILED",
                score=1.0 if passed else 0.0,
                input_json={"sql": case["sql"]},
                expected_json={"expected_safe": expected_safe, "expected_reason_contains": case.get("expected_reason_contains")},
                actual_json={"safe": result.safe, "sql": result.sql, "reason": result.reason},
                error_message=None if passed else "SQL Guardrails expectation mismatch",
                duration_ms=int((time.perf_counter() - case_started) * 1000),
            )
        )
    return persist_eval_run(
        db,
        "SQL_GUARDRAILS",
        results,
        {"false_negative": false_negative, "false_positive": false_positive},
        created_by,
        started,
    )
