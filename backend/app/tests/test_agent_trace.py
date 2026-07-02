from app.main import app


def test_run_trace_and_step_routes_exist() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/runs" in paths
    assert "/api/runs/{run_id}" in paths
    assert "/api/runs/{run_id}/steps" in paths
    assert "/api/runs/{run_id}/traces" in paths
