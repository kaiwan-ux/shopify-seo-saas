"""Vector store abstraction — swappable backend."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class VectorPoint(BaseModel):
    """A vector point to upsert."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    vector: list[float]
    payload: dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    """A single search result."""

    id: str
    score: float
    payload: dict[str, Any]


class CollectionStats(BaseModel):
    """Collection statistics."""

    name: str
    points_count: int
    vectors_count: int
    status: str


class BaseVectorStore(ABC):
    """Abstract vector store — implement for Qdrant, Pinecone, etc."""

    @abstractmethod
    async def ensure_collection(self, name: str, dimensions: int) -> None:
        """Create collection if it doesn't exist."""

    @abstractmethod
    async def upsert(self, collection: str, points: list[VectorPoint]) -> int:
        """Upsert vectors, return count upserted."""

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        limit: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Similarity search with optional metadata filters."""

    @abstractmethod
    async def delete(self, collection: str, point_ids: list[str]) -> int:
        """Delete points by ID."""

    @abstractmethod
    async def get_stats(self, collection: str) -> CollectionStats:
        """Return collection statistics."""

    @abstractmethod
    async def collection_exists(self, collection: str) -> bool:
        """Check if collection exists."""
