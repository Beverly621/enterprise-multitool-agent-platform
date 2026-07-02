from types import SimpleNamespace

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from fastapi.testclient import TestClient


def _user(role_name: str = "User"):
    role = SimpleNamespace(name=role_name, permissions=[])
    return SimpleNamespace(id=1, email="user@example.com", is_active=True, roles=[role])


def test_agent_chat_route_returns_runtime_response(monkeypatch) -> None:
    async def fake_run_agent(db, user, query, session_id=None, kb_id=None):
        return {
            "run_id": "run_test",
            "intent": "GENERAL_CHAT",
            "status": "SUCCESS",
            "answer": "hello",
            "approval_id": None,
            "trace_url": "/api/runs/run_test/traces",
            "citations": [],
            "generated_sql": None,
            "sql_result": None,
            "tool_results": [],
            "error": None,
        }

    app.dependency_overrides[get_current_user] = lambda: _user()
    app.dependency_overrides[get_db] = lambda: None
    monkeypatch.setattr("app.api.agent_chat.run_agent", fake_run_agent)
    try:
        response = TestClient(app).post(
            "/api/agent/chat",
            json={"session_id": "s1", "query": "你好"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["run_id"] == "run_test"
    assert response.json()["data"]["trace_url"] == "/api/runs/run_test/traces"
