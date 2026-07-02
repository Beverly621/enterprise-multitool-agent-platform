from types import SimpleNamespace

from app.agent.nodes.report_node import run_report_node


class FakeDB:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None


def test_report_node_generates_required_sections() -> None:
    run = SimpleNamespace(run_id="run_report", status="CREATED", current_step=None, updated_at=None)
    state = {
        "query": "结合最近 30 天订单异常数据和售后知识库生成一份分析报告",
        "sql_result": {"row_count": 3},
        "sql_answer": "异常订单集中在 SP。",
        "retrieved_chunks": [{"filename": "policy.md", "chunk_index": 0}],
        "citations": [{"document_id": 1, "chunk_index": 0}],
    }

    result = run_report_node(FakeDB(), run, state, SimpleNamespace(id=1))

    assert "# 最近 30 天订单异常分析报告" in result["report"]
    assert "## 一、数据来源" in result["report"]
    assert "## 七、生成时间" in result["report"]
