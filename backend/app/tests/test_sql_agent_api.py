from types import SimpleNamespace

from app.api.sql_agent import _require_sql_access
from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.schemas.sql_agent import SQLAgentQueryResponse
from fastapi.testclient import TestClient


def _user(role_name: str = "User", permission_codes: list[str] | None = None):
    permissions = [SimpleNamespace(code=code) for code in (permission_codes or [])]
    role = SimpleNamespace(name=role_name, permissions=permissions)
    return SimpleNamespace(id=1, email="user@example.com", is_active=True, roles=[role])


def test_guest_has_no_sql_agent_access() -> None:
    try:
        _require_sql_access(_user("Guest", []))
    except Exception as exc:
        assert "SQL Agent" in str(exc)
    else:
        raise AssertionError("Guest should not access SQL Agent")


def test_user_can_call_sql_agent_query(monkeypatch) -> None:
    def fake_run_sql_agent(db, user, question):
        return SQLAgentQueryResponse(
            run_id="run_test",
            question=question,
            generated_sql="SELECT state, COUNT(*) AS cnt FROM demo_orders GROUP BY state LIMIT 100",
            safe=True,
            columns=["state", "cnt"],
            rows=[{"state": "SP", "cnt": 3}],
            row_count=1,
            duration_ms=1,
            answer="异常订单主要集中在 SP。",
            trace_url="/api/runs/run_test/traces",
        )

    app.dependency_overrides[get_current_user] = lambda: _user("User", ["sql_agent:execute"])
    app.dependency_overrides[get_db] = lambda: None
    monkeypatch.setattr("app.api.sql_agent.run_sql_agent", fake_run_sql_agent)

    try:
        response = TestClient(app).post(
            "/api/sql-agent/query",
            json={"question": "哪个地区异常最多？"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["safe"] is True
    assert data["rows"][0]["state"] == "SP"


def test_dangerous_sql_agent_query_can_return_blocked(monkeypatch) -> None:
    def fake_run_sql_agent(db, user, question):
        return SQLAgentQueryResponse(
            run_id="run_blocked",
            question=question,
            generated_sql="DROP TABLE demo_orders;",
            safe=False,
            blocked_reason="Only SELECT statements are allowed.",
            answer="该查询涉及危险 SQL 操作，已被系统安全策略拦截。",
            trace_url="/api/runs/run_blocked/traces",
        )

    app.dependency_overrides[get_current_user] = lambda: _user("User", ["sql_agent:execute"])
    app.dependency_overrides[get_db] = lambda: None
    monkeypatch.setattr("app.api.sql_agent.run_sql_agent", fake_run_sql_agent)

    try:
        response = TestClient(app).post(
            "/api/sql-agent/query",
            json={"question": "DROP TABLE demo_orders"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["safe"] is False
    assert data["blocked_reason"]
