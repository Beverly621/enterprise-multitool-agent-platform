import pytest
from app.services.tool_validation_service import ToolValidationError, validate_tool_args
from app.tools import get_builtin_tools


def test_validation_accepts_expected_args() -> None:
    schema = get_builtin_tools()["create_todo"].metadata.schema_json

    validate_tool_args(schema, {"title": "Follow up", "priority": "HIGH"})


def test_validation_rejects_missing_args() -> None:
    schema = get_builtin_tools()["create_todo"].metadata.schema_json

    with pytest.raises(ToolValidationError):
        validate_tool_args(schema, {"priority": "LOW"})


def test_validation_rejects_extra_args() -> None:
    schema = get_builtin_tools()["create_todo"].metadata.schema_json

    with pytest.raises(ToolValidationError):
        validate_tool_args(schema, {"title": "Follow up", "shell": "python -c '...'"})
