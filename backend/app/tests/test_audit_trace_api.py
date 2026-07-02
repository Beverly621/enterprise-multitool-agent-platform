from app.main import app


def test_audit_and_trace_routes_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/audit" in paths
    assert "/api/runs/{run_id}/traces" in paths
