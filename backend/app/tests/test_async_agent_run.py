from types import SimpleNamespace

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models.agent_run import AgentRun
from app.models.task_progress import TaskProgress
from app.services.async_run_service import submit_async_agent_run
from fastapi.testclient import TestClient


class FakeDB:
    def __init__(self):
        self.items = []
        self.commits = 0

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None

    def commit(self):
        self.commits += 1

    def scalar(self, statement):
        return None


def _user(role_name: str = "User"):
    role = SimpleNamespace(name=role_name, permissions=[])
    return SimpleNamespace(id=1, email="user@example.com", is_active=True, roles=[role])


def test_submit_async_agent_run_returns_task_id_without_waiting(monkeypatch) -> None:
    submitted = {}

    def fake_apply_async(args=None, task_id=None, **kwargs):
        submitted["args"] = args
        submitted["task_id"] = task_id
        return SimpleNamespace(id=task_id)

    monkeypatch.setattr("app.tasks.agent_tasks.run_agent_async_task.apply_async", fake_apply_async)

    db = FakeDB()
    response = submit_async_agent_run(
        db,
        _user(),
        query="生成一份订单异常分析报告",
        session_id="s1",
        kb_id=1,
        idempotency_key="demo-report-001",
    )

    assert response["run_id"].startswith("run_")
    assert response["task_id"].startswith("task_")
    assert response["status"] == "PENDING"
    assert submitted["task_id"] == response["task_id"]
    assert any(isinstance(item, AgentRun) for item in db.items)
    assert any(isinstance(item, TaskProgress) for item in db.items)


def test_agent_chat_async_mode_uses_submit_service(monkeypatch) -> None:
    def fake_submit_async_agent_run(
        db,
        user,
        query,
        session_id=None,
        kb_id=None,
        idempotency_key=None,
    ):
        return {
            "run_id": "run_async",
            "task_id": "task_async",
            "status": "PENDING",
            "message": "Agent task has been submitted.",
            "progress_url": "/api/runs/run_async/progress",
            "trace_url": "/api/runs/run_async/traces",
            "idempotent": False,
        }

    app.dependency_overrides[get_current_user] = lambda: _user()
    app.dependency_overrides[get_db] = lambda: None
    monkeypatch.setattr("app.api.agent_chat.submit_async_agent_run", fake_submit_async_agent_run)
    try:
        response = TestClient(app).post(
            "/api/agent/chat",
            json={
                "session_id": "s1",
                "query": "生成一份订单异常分析报告",
                "async_mode": True,
                "idempotency_key": "demo-report-001",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data"]["task_id"] == "task_async"
