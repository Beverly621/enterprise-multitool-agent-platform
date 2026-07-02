from app.main import app
from app.models.report import Report
from app.services.report_history_service import save_report_history


class FakeDB:
    def __init__(self):
        self.items = []

    def scalar(self, statement):
        return None

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None


def test_async_report_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/reports" in paths
    assert "/api/reports/{report_id}" in paths
    assert "/api/runs/{run_id}/report" in paths
    assert "/api/reports/{report_id}/export" in paths
    assert "/api/runs/{run_id}/progress" in paths
    assert "/api/tasks/{task_id}/progress" in paths


def test_multistep_report_can_be_saved_with_report_saved_trace() -> None:
    db = FakeDB()

    save_report_history(
        db,
        run_id="run_1",
        user_id=1,
        title="业务分析报告",
        report_type="agent_multistep_report",
        content_markdown="# 业务分析报告\n\n## 六、引用来源",
        source_metadata_json={"intent": "MULTI_STEP_REPORT"},
    )

    assert any(isinstance(item, Report) for item in db.items)
    assert any(getattr(item, "event_name", None) == "REPORT_SAVED" for item in db.items)
