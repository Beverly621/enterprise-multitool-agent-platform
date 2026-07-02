from types import SimpleNamespace

import pytest
from app.models.report import Report
from app.services.report_history_service import get_report_for_user, save_report_history
from fastapi import HTTPException


class FakeDB:
    def __init__(self, scalar_item=None):
        self.scalar_item = scalar_item
        self.items = []

    def scalar(self, statement):
        return self.scalar_item

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None


def _user(user_id=1, role_name="User"):
    role = SimpleNamespace(name=role_name, permissions=[])
    return SimpleNamespace(id=user_id, roles=[role])


def test_report_generation_writes_report_history() -> None:
    db = FakeDB()

    report = save_report_history(
        db,
        run_id="run_1",
        user_id=1,
        title="业务分析报告",
        report_type="agent_multistep_report",
        content_markdown="# 业务分析报告\n\n## 一、数据来源",
    )

    assert report.report_id.startswith("report_")
    assert any(isinstance(item, Report) for item in db.items)


def test_user_can_only_view_own_report() -> None:
    report = Report(
        report_id="report_1",
        run_id="run_1",
        user_id=2,
        title="报告",
        report_type="custom",
        content_markdown="# 报告",
    )

    with pytest.raises(HTTPException):
        get_report_for_user(FakeDB(report), "report_1", _user(user_id=1))

    assert get_report_for_user(FakeDB(report), "report_1", _user(user_id=2)) is report
    assert (
        get_report_for_user(FakeDB(report), "report_1", _user(user_id=9, role_name="Admin"))
        is report
    )
