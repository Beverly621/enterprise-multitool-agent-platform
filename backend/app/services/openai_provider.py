from app.services.mock_provider import MockEmbeddingProvider, MockLLMProvider
from app.services.provider_base import ChatMessage


class OpenAIProvider(MockLLMProvider):
    name = "openai"

    def chat(self, messages: list[ChatMessage]) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            return super().chat(messages)

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": message.role, "content": message.content} for message in messages],
        )
        return response.choices[0].message.content or ""


class OpenAIEmbeddingProvider(MockEmbeddingProvider):
    name = "openai"

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import OpenAI
        except ImportError:
            return super().embed(texts)

        client = OpenAI()
        response = client.embeddings.create(model="text-embedding-3-small", input=texts)
        return [item.embedding for item in response.data]

