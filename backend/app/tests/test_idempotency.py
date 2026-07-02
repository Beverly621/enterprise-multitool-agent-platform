from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from app.services.idempotency_service import get_reusable_idempotency_key, request_hash
from fastapi import HTTPException


class FakeDB:
    def __init__(self, item):
        self.item = item

    def scalar(self, statement):
        return self.item


def test_same_idempotency_key_returns_existing_task() -> None:
    payload_hash = request_hash({"query": "生成报告", "async_mode": True})
    item = SimpleNamespace(
        idempotency_key="demo",
        user_id=1,
        request_hash=payload_hash,
        run_id="run_1",
        task_id="task_1",
        status="PENDING",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    reused = get_reusable_idempotency_key(FakeDB(item), 1, "demo", payload_hash)

    assert reused.run_id == "run_1"
    assert reused.task_id == "task_1"


def test_same_idempotency_key_with_different_payload_conflicts() -> None:
    item = SimpleNamespace(
        request_hash=request_hash({"query": "A"}),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    with pytest.raises(HTTPException):
        get_reusable_idempotency_key(FakeDB(item), 1, "demo", request_hash({"query": "B"}))
