from app.services.tool_registry import normalize_tool_name
from app.tools import get_builtin_tools


def test_builtin_registry_contains_phase_four_tools() -> None:
    tools = get_builtin_tools()

    assert set(tools) == {
        "search_knowledge_base",
        "execute_safe_sql",
        "query_order_status",
        "query_after_sales",
        "generate_report",
        "send_email_draft",
        "create_todo",
    }
    assert tools["execute_safe_sql"].metadata.permission_level == "Developer"
    assert tools["send_email_draft"].metadata.require_approval is True
    assert "question" in tools["execute_safe_sql"].metadata.schema_json["properties"]
    assert tools["execute_safe_sql"].metadata.schema_json["required"] == []
    assert "data_summary" in tools["generate_report"].metadata.schema_json["properties"]


def test_normalize_tool_name() -> None:
    assert normalize_tool_name(" Query Order Status ") == "query_order_status"
