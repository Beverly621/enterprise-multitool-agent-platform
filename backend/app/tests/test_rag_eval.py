from app.services.rag_eval_service import run_rag_eval


def test_rag_eval_dataset_has_at_least_ten_cases_and_runs_without_db() -> None:
    result = run_rag_eval(None)

    assert result["total_cases"] >= 10
    assert result["passed_cases"] == result["total_cases"]
    assert result["pass_rate"] == 1
