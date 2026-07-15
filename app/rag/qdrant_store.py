"""Qdrant vector store implementation."""

from typing import Any

from loguru import logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config.settings import Settings, get_settings
from app.rag.vector_store import (
    BaseVectorStore,
    CollectionStats,
    VectorPoint,
    VectorSearchResult,
)


class QdrantVectorStore(BaseVectorStore):
    """Production async Qdrant client with collection management."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = AsyncQdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
        )
        self._prefix = self.settings.qdrant_collection_prefix

    def _full_name(self, collection: str) -> str:
        return f"{self._prefix}_{collection}"

    async def ensure_collection(self, name: str, dimensions: int) -> None:
        full_name = self._full_name(name)
        exists = await self._client.collection_exists(full_name)
        if not exists:
            await self._client.create_collection(
                collection_name=full_name,
                vectors_config=VectorParams(size=dimensions, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection: {}", full_name)

    async def upsert(self, collection: str, points: list[VectorPoint]) -> int:
        full_name = self._full_name(collection)
        qdrant_points = [
            PointStruct(id=p.id, vector=p.vector, payload=p.payload) for p in points
        ]
        await self._client.upsert(collection_name=full_name, points=qdrant_points)
        return len(qdrant_points)

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        limit: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        full_name = self._full_name(collection)
        qdrant_filter = self._build_filter(filters) if filters else None

        results = await self._client.search(
            collection_name=full_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qdrant_filter,
        )

        return [
            VectorSearchResult(
                id=str(r.id),
                score=r.score,
                payload=r.payload or {},
            )
            for r in results
        ]

    async def delete(self, collection: str, point_ids: list[str]) -> int:
        full_name = self._full_name(collection)
        await self._client.delete(collection_name=full_name, points_selector=point_ids)
        return len(point_ids)

    async def get_stats(self, collection: str) -> CollectionStats:
        full_name = self._full_name(collection)
        info = await self._client.get_collection(full_name)
        return CollectionStats(
            name=full_name,
            points_count=info.points_count or 0,
            vectors_count=info.vectors_count or 0,
            status=str(info.status),
        )

    async def collection_exists(self, collection: str) -> bool:
        return await self._client.collection_exists(self._full_name(collection))

    @staticmethod
    def _build_filter(filters: dict[str, Any]) -> Filter:
        conditions = [
            FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()
        ]
        return Filter(must=conditions)


def get_vector_store(settings: Settings | None = None) -> BaseVectorStore:
    """Factory — returns configured vector store (currently Qdrant only)."""
    return QdrantVectorStore(settings)
