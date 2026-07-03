from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.metric import EvalResult, EvalRun


@dataclass(slots=True)
class EvalCaseResult:
    case_id: str
    status: str
    score: float
    input_json: dict[str, Any]
    expected_json: dict[str, Any]
    actual_json: dict[str, Any]
    error_message: str | None
    duration_ms: int


def persist_eval_run(
    db: Session | None,
    case_type: str,
    results: list[EvalCaseResult],
    summary: dict[str, Any] | None = None,
    created_by: int | None = None,
    started: float | None = None,
) -> dict[str, Any]:
    total = len(results)
    passed = sum(1 for result in results if result.status == "PASSED")
    failed = total - passed
    eval_run_id = f"eval_{uuid.uuid4().hex}"
    duration_ms = int((time.perf_counter() - (started or time.perf_counter())) * 1000)
    payload = {
        "eval_run_id": eval_run_id,
        "case_type": case_type,
        "status": "PASSED" if failed == 0 else "FAILED",
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "pass_rate": round(passed / total, 4) if total else 0,
        "duration_ms": duration_ms,
        "summary": summary or {},
        "results": [asdict(result) for result in results],
    }
    if db is None:
        return payload
    db.add(
        EvalRun(
            eval_run_id=eval_run_id,
            case_type=case_type,
            status=payload["status"],
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            pass_rate=payload["pass_rate"],
            duration_ms=duration_ms,
            summary_json=summary or {},
            created_by=created_by,
        )
    )
    for result in results:
        db.add(
            EvalResult(
                eval_run_id=eval_run_id,
                case_id=result.case_id,
                status=result.status,
                score=result.score,
                input_json=result.input_json,
                expected_json=result.expected_json,
                actual_json=result.actual_json,
                error_message=result.error_message,
                duration_ms=result.duration_ms,
            )
        )
    db.commit()
    return payload
