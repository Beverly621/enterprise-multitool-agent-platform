import hashlib
import random

from app.core.config import settings
from app.services.provider_base import ChatMessage, EmbeddingProvider, LLMProvider


class MockLLMProvider(LLMProvider):
    name = "mock"

    def chat(self, messages: list[ChatMessage]) -> str:
        latest = messages[-1].content if messages else ""
        return f"[MockLLM] Received: {latest[:300]}"


class MockEmbeddingProvider(EmbeddingProvider):
    name = "mock"

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
            rng = random.Random(seed)
            vectors.append([rng.uniform(-1.0, 1.0) for _ in range(settings.vector_dimension)])
        return vectors

