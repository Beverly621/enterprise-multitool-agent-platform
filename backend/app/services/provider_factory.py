import logging

from app.core.config import settings
from app.services.mock_provider import MockEmbeddingProvider, MockLLMProvider
from app.services.openai_provider import OpenAIEmbeddingProvider, OpenAIProvider
from app.services.provider_base import EmbeddingProvider, LLMProvider

logger = logging.getLogger(__name__)


def get_llm_provider() -> LLMProvider:
    provider = settings.default_llm_provider.lower()
    if provider == "openai" and settings.openai_api_key:
        return OpenAIProvider()
    if provider != "mock":
        logger.warning(
            "LLM provider %s is unavailable or missing API key; falling back to mock provider.",
            provider,
        )
    return MockLLMProvider()


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.default_embedding_provider.lower()
    if provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider()
    if provider != "mock":
        logger.warning(
            "Embedding provider %s is unavailable or missing API key; "
            "falling back to mock provider.",
            provider,
        )
    return MockEmbeddingProvider()
