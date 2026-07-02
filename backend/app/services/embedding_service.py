from app.services.provider_factory import get_embedding_provider


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return get_embedding_provider().embed(texts)
