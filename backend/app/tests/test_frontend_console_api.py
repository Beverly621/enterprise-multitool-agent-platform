from app.main import app


def test_frontend_console_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/dashboard/summary" in paths
    assert "/api/tasks" in paths
    assert "/api/tool-calls" in paths
    assert "/api/kb/{kb_id}" in paths
    assert "/api/kb/{kb_id}/documents" in paths
