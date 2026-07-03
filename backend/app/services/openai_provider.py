from app.services.mock_provider import MockEmbeddingProvider, MockLLMProvider
from app.services.provider_base import ChatMessage
from app.services.provider_metrics_service import time_provider_call
import time


class OpenAIProvider(MockLLMProvider):
    name = "openai"
    model_name = "gpt-4.1-mini"

    def chat(self, messages: list[ChatMessage]) -> str:
        started = time.perf_counter()
        input_text = "\n".join(message.content for message in messages)
        try:
            from openai import OpenAI
        except ImportError:
            return super().chat(messages)

        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": message.role, "content": message.content} for message in messages],
            )
            answer = response.choices[0].message.content or ""
            time_provider_call(self.name, self.model_name, input_text, answer, started=started)
            return answer
        except Exception as exc:
            time_provider_call(
                self.name,
                self.model_name,
                input_text,
                error=exc,
                status="FAILED",
                started=started,
            )
            raise


class OpenAIEmbeddingProvider(MockEmbeddingProvider):
    name = "openai"
    model_name = "text-embedding-3-small"

    def embed(self, texts: list[str]) -> list[list[float]]:
        started = time.perf_counter()
        input_text = "\n".join(texts)
        try:
            from openai import OpenAI
        except ImportError:
            return super().embed(texts)

        client = OpenAI()
        try:
            response = client.embeddings.create(model=self.model_name, input=texts)
            vectors = [item.embedding for item in response.data]
            time_provider_call(
                self.name,
                self.model_name,
                input_text,
                f"{len(vectors)} vectors",
                started=started,
                request_type="EMBEDDING",
            )
            return vectors
        except Exception as exc:
            time_provider_call(
                self.name,
                self.model_name,
                input_text,
                error=exc,
                status="FAILED",
                started=started,
                request_type="EMBEDDING",
            )
            raise
