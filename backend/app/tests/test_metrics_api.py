from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app


def _developer():
    role = SimpleNamespace(name="Developer", permissions=[])
    return SimpleNamespace(id=1, email="dev@example.com", is_active=True, roles=[role])


def test_metrics_and_eval_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/metrics/summary" in paths
    assert "/api/metrics/agent-runs" in paths
    assert "/api/metrics/providers" in paths
    assert "/api/evals/runs" in paths
    assert "/api/evals/runs/{eval_run_id}" in paths


def test_metrics_summary_api_enforces_auth_and_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.metrics.metrics_service.summary_metrics",
        lambda db, user_id: {"agent_run_success_rate": 1, "provider_calls_total": 1},
    )
    app.dependency_overrides[get_current_user] = _developer
    app.dependency_overrides[get_db] = lambda: None
    try:
        response = TestClient(app).get("/api/metrics/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["provider_calls_total"] == 1
