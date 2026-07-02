from types import SimpleNamespace

import pytest
from app.agent.runtime import response_from_state, run_agent_chat


class FakeDB:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None

    def scalar(self, statement):
        return next((item for item in self.items if getattr(item, "run_id", None)), None)


def _user(role_name: str = "User"):
    role = SimpleNamespace(name=role_name, permissions=[])
    return SimpleNamespace(id=1, email="user@example.com", is_active=True, roles=[role])


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_agent_runtime_general_chat_success() -> None:
    state = await run_agent_chat(FakeDB(), _user(), "你好，介绍一下你能做什么？")
    response = response_from_state(state)

    assert response["intent"] == "GENERAL_CHAT"
    assert response["status"] == "SUCCESS"
    assert "企业级多工具 Agent" in response["answer"]


@pytest.mark.anyio
async def test_agent_runtime_guest_sql_fails_structurally() -> None:
    state = await run_agent_chat(FakeDB(), _user("Guest"), "哪个地区的订单异常最多？")
    response = response_from_state(state)

    assert response["intent"] == "SQL_QUERY"
    assert response["status"] == "FAILED"
    assert "Developer" in response["answer"]
