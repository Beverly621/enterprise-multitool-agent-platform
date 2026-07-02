from app.services.mock_provider import MockEmbeddingProvider, MockLLMProvider


def test_mock_llm_returns_non_empty_text() -> None:
    provider = MockLLMProvider()

    assert provider.chat([]).startswith("[MockLLM]")


def test_mock_embedding_dimension_matches_settings() -> None:
    vector = MockEmbeddingProvider().embed(["hello"])[0]

    assert len(vector) == 1536
    assert vector == MockEmbeddingProvider().embed(["hello"])[0]
