import hashlib
import random
import time

from app.core.config import settings
from app.services.provider_base import ChatMessage, EmbeddingProvider, LLMProvider
from app.services.provider_metrics_service import time_provider_call


class MockLLMProvider(LLMProvider):
    name = "mock"
    model_name = "mock-llm"

    def chat(self, messages: list[ChatMessage]) -> str:
        started = time.perf_counter()
        input_text = "\n".join(message.content for message in messages)
        latest = messages[-1].content if messages else ""
        answer = f"[MockLLM] Received: {latest[:300]}"
        time_provider_call(
            self.name,
            self.model_name,
            input_text=input_text,
            output_text=answer,
            started=started,
            request_type="LLM_CHAT",
        )
        return answer


class MockEmbeddingProvider(EmbeddingProvider):
    name = "mock"
    model_name = "mock-embedding"

    def embed(self, texts: list[str]) -> list[list[float]]:
        started = time.perf_counter()
        vectors: list[list[float]] = []
        for text in texts:
            seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
            rng = random.Random(seed)
            vectors.append([rng.uniform(-1.0, 1.0) for _ in range(settings.vector_dimension)])
        time_provider_call(
            self.name,
            self.model_name,
            input_text="\n".join(texts),
            output_text=f"{len(vectors)} vectors",
            started=started,
            request_type="EMBEDDING",
        )
        return vectors
