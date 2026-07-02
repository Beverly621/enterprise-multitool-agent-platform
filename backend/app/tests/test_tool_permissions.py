from types import SimpleNamespace

from app.models.tool import AgentTool
from app.services.tool_permission_service import can_invoke_tool, highest_role_level


def _user_with_role(role_name: str):
    return SimpleNamespace(roles=[SimpleNamespace(name=role_name, permissions=[])])


def test_role_order() -> None:
    assert highest_role_level(_user_with_role("Guest")) < highest_role_level(
        _user_with_role("User")
    )
    assert highest_role_level(_user_with_role("User")) < highest_role_level(
        _user_with_role("Developer")
    )
    assert highest_role_level(_user_with_role("Developer")) < highest_role_level(
        _user_with_role("Admin")
    )


def test_developer_tool_blocks_user_role() -> None:
    tool = AgentTool(
        name="execute_safe_sql",
        schema_json={"type": "object"},
        permission_level="Developer",
    )

    assert can_invoke_tool(_user_with_role("User"), tool) is False
    assert can_invoke_tool(_user_with_role("Developer"), tool) is True
