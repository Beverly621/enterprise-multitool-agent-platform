from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def chat(self, messages: list[ChatMessage]) -> str:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    name: str

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

