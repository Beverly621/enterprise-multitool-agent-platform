from typing import Any

from pydantic import BaseModel


class EvalRunSummary(BaseModel):
    eval_run_id: str
    case_type: str
    status: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    duration_ms: int
    summary_json: dict[str, Any] | None = None


class EvalResultItem(BaseModel):
    case_id: str
    status: str
    score: float
    input_json: dict[str, Any] | None = None
    expected_json: dict[str, Any] | None = None
    actual_json: dict[str, Any] | None = None
    error_message: str | None = None
    duration_ms: int
