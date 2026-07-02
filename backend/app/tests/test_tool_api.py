from app.main import app


def test_tool_calling_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/tools/{tool_name}/invoke" in paths
    assert "/api/approvals/{approval_id}/approve" in paths
    assert "/api/tool-calls/{tool_call_id}" in paths
    assert "/api/runs/{run_id}/tool-calls" in paths
