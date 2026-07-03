from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.services.base_eval_service import EvalCaseResult, persist_eval_run
from app.services.eval_case_loader import load_eval_cases
from app.services.intent_router_service import route_intent


def run_agent_eval(db: Session | None = None, created_by: int | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    results: list[EvalCaseResult] = []
    for case in load_eval_cases("agent"):
        case_started = time.perf_counter()
        route = route_intent(case["query"])
        expected_intent = case["expected_intent"]
        passed = route.intent == expected_intent
        results.append(
            EvalCaseResult(
                case_id=case["case_id"],
                status="PASSED" if passed else "FAILED",
                score=1.0 if passed else 0.0,
                input_json={"query": case["query"]},
                expected_json={"expected_intent": expected_intent, "expected_status": case.get("expected_status")},
                actual_json={"intent": route.intent, "confidence": route.confidence, "reason": route.reason},
                error_message=None if passed else "Intent routing regression",
                duration_ms=int((time.perf_counter() - case_started) * 1000),
            )
        )
    return persist_eval_run(db, "AGENT_RUN", results, {"mode": "intent_regression"}, created_by, started)
