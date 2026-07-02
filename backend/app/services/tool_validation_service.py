from __future__ import annotations

from typing import Any

from jsonschema import Draft7Validator, FormatChecker


class ToolValidationError(ValueError):
    pass


def validate_tool_args(schema_json: dict[str, Any], args: dict[str, Any]) -> None:
    validator = Draft7Validator(schema_json, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(args), key=lambda error: list(error.path))
    if errors:
        message = "; ".join(error.message for error in errors)
        raise ToolValidationError(message)

    properties = schema_json.get("properties")
    if schema_json.get("additionalProperties") is False and isinstance(properties, dict):
        extra_keys = sorted(set(args) - set(properties))
        if extra_keys:
            raise ToolValidationError(f"Unexpected argument(s): {', '.join(extra_keys)}")


def validate_tool_schema(schema_json: dict[str, Any]) -> None:
    try:
        Draft7Validator.check_schema(schema_json)
    except Exception as exc:
        raise ToolValidationError(f"Invalid tool schema: {exc}") from exc
