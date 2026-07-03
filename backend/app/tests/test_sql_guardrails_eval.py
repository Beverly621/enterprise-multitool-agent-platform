from app.services.sql_guardrails_eval_service import run_sql_guardrails_eval


def test_sql_guardrails_eval_blocks_all_dangerous_sql() -> None:
    result = run_sql_guardrails_eval(None)

    assert result["total_cases"] >= 20
    assert result["summary"]["false_negative"] == 0
    assert result["status"] == "PASSED"
