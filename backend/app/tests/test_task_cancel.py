from types import SimpleNamespace

import pytest
from app.models.agent_run import AgentRun
from app.models.task_progress import TaskProgress
from app.services.task_progress_service import cancel_task_progress
from fastapi import HTTPException


class FakeDB:
    def __init__(self, run=None):
        self.run = run
        self.items = []

    def scalar(self, statement):
        return self.run

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None


def _user(role_name: str = "User"):
    role = SimpleNamespace(name=role_name, permissions=[])
    return SimpleNamespace(id=1, roles=[role])


def test_running_task_can_be_cancelled() -> None:
    run = AgentRun(run_id="run_1", user_id=1, query="q", status="RUNNING")
    task = TaskProgress(
        task_id="task_1",
        run_id="run_1",
        user_id=1,
        task_type="AGENT_RUN",
        status="RUNNING",
        progress=20,
    )

    cancel_task_progress(FakeDB(run), task, _user())

    assert task.status == "CANCELLED"
    assert run.status == "CANCELLED"


def test_success_task_cannot_be_cancelled() -> None:
    task = TaskProgress(
        task_id="task_2",
        user_id=1,
        task_type="AGENT_RUN",
        status="SUCCESS",
        progress=100,
    )

    with pytest.raises(HTTPException):
        cancel_task_progress(FakeDB(), task, _user())
