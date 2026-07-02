from app.services.embedding_service import embed_texts


def test_mock_embeddings_are_deterministic() -> None:
    first = embed_texts(["same text"])[0]
    second = embed_texts(["same text"])[0]

    assert first == second
    assert len(first) > 0

