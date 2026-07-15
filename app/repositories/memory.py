import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory_entry import MemoryEntry
from app.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[MemoryEntry]):
    model = MemoryEntry

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        key: str,
        content: str,
        memory_type: str,
        user_id: uuid.UUID | None = None,
        store_id: uuid.UUID | None = None,
        workflow_run_id: uuid.UUID | None = None,
        metadata_: dict[str, Any] | None = None,
        qdrant_point_id: str | None = None,
        collection_name: str | None = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            key=key,
            content=content,
            memory_type=memory_type,
            user_id=user_id,
            store_id=store_id,
            workflow_run_id=workflow_run_id,
            metadata_=metadata_,
            qdrant_point_id=qdrant_point_id,
            collection_name=collection_name,
        )
        return await super().create(entry)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        memory_type: str | None = None,
        limit: int = 20,
    ) -> list[MemoryEntry]:
        query = select(MemoryEntry).where(MemoryEntry.user_id == user_id)
        if memory_type:
            query = query.where(MemoryEntry.memory_type == memory_type)
        query = query.order_by(MemoryEntry.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
