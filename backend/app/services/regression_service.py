from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.services.agent_eval_service import run_agent_eval
from app.services.base_eval_service import EvalCaseResult, persist_eval_run
from app.services.eval_case_loader import load_eval_cases
from app.services.sql_guardrails import validate_sql
from app.services.intent_router_service import route_intent


def run_regression(db: Session | None = None, created_by: int | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    results: list[EvalCaseResult] = []
    for case in load_eval_cases("regression"):
        case_started = time.perf_counter()
        actual: dict[str, Any] = {}
        expected = case["expected"]
        if "query" in case:
            route = route_intent(case["query"])
            actual["intent"] = route.intent
        if "sql" in case:
            guardrail = validate_sql(case["sql"])
            actual["sql_safe"] = guardrail.safe
        passed = all(actual.get(key) == value for key, value in expected.items())
        results.append(
            EvalCaseResult(
                case_id=case["case_id"],
                status="PASSED" if passed else "FAILED",
                score=1.0 if passed else 0.0,
                input_json={key: case[key] for key in ("query", "sql") if key in case},
                expected_json=expected,
                actual_json=actual,
                error_message=None if passed else "Core demo regression mismatch",
                duration_ms=int((time.perf_counter() - case_started) * 1000),
            )
        )
    return persist_eval_run(db, "REGRESSION", results, {"agent_eval_available": True}, created_by, started)
