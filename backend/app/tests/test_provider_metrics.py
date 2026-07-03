from app.services.mock_provider import MockEmbeddingProvider, MockLLMProvider
from app.services.provider_base import ChatMessage
from app.services.provider_metrics_service import provider_metrics_scope


class FakeDB:
    def __init__(self):
        self.added = []

    def add(self, item):
        self.added.append(item)


def test_mock_llm_provider_records_zero_cost_metric() -> None:
    db = FakeDB()

    with provider_metrics_scope(db=db, run_id="run_test", user_id=1, request_type="LLM_CHAT"):
        answer = MockLLMProvider().chat([ChatMessage(role="user", content="hello")])

    assert answer.startswith("[MockLLM]")
    assert len(db.added) == 1
    metric = db.added[0]
    assert metric.provider_name == "mock"
    assert metric.request_type == "LLM_CHAT"
    assert metric.estimated_cost == 0
    assert metric.run_id == "run_test"


def test_mock_embedding_provider_records_embedding_metric() -> None:
    db = FakeDB()

    with provider_metrics_scope(db=db, run_id="run_test", user_id=1):
        vectors = MockEmbeddingProvider().embed(["hello"])

    assert len(vectors) == 1
    assert db.added[0].request_type == "EMBEDDING"
    assert db.added[0].estimated_cost == 0
