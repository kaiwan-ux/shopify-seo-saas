"""Embedding provider abstraction."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class EmbeddingResult(BaseModel):
    """Single embedding result."""

    text: str
    vector: list[float]
    model: str
    dimensions: int


class BaseEmbeddingProvider(ABC):
    """Abstract embedding provider."""

    @abstractmethod
    async def embed_text(self, text: str) -> EmbeddingResult:
        """Embed a single text string."""

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed multiple texts."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return model identifier."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return vector dimensions."""
