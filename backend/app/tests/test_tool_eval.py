from app.services.tool_eval_service import run_tool_eval


def test_tool_eval_checks_approval_permissions_and_guardrails() -> None:
    result = run_tool_eval(None)

    assert result["total_cases"] >= 10
    assert result["status"] == "PASSED"
