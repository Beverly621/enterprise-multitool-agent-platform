from app.services.agent_eval_service import run_agent_eval
from app.services.regression_service import run_regression


def test_agent_eval_dataset_routes_core_intents() -> None:
    result = run_agent_eval(None)

    assert result["total_cases"] >= 12
    assert result["status"] == "PASSED"


def test_regression_dataset_runs_without_db() -> None:
    result = run_regression(None)

    assert result["total_cases"] >= 12
    assert result["status"] == "PASSED"
