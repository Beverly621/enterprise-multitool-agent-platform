from app.services.tool_executor import _sanitize_args, _summarize_result


def test_sanitizes_sensitive_tool_args() -> None:
    args = _sanitize_args({"api_key": "secret", "query": "hello"})

    assert args == {"api_key": "***", "query": "hello"}


def test_summarizes_large_row_results() -> None:
    result = _summarize_result({"rows": [{"id": index} for index in range(30)]})

    assert len(result["rows"]) == 20
    assert result["truncated"] is True
