import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.base import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    model = Collection

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def upsert(self, store_id: uuid.UUID, shopify_id: str, data: dict[str, Any]) -> Collection:
        result = await self.session.execute(
            select(Collection).where(
                Collection.store_id == store_id, Collection.shopify_id == shopify_id
            )
        )
        entity = result.scalar_one_or_none()
        if entity is None:
            entity = Collection(store_id=store_id, shopify_id=shopify_id, **data)
            return await self.create(entity)
        for key, value in data.items():
            setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity



    async def get_by_store_and_id(self, store_id: uuid.UUID, entity_id: uuid.UUID) -> Collection | None:
        result = await self.session.execute(
            select(Collection).where(Collection.store_id == store_id, Collection.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_store_and_shopify_id(self, store_id: uuid.UUID, shopify_id: str) -> Collection | None:
        result = await self.session.execute(
            select(Collection).where(Collection.store_id == store_id, Collection.shopify_id == shopify_id)
        )
        return result.scalar_one_or_none()

    async def list_by_store(self, store_id: uuid.UUID, limit: int = 50) -> list[Collection]:
        result = await self.session.execute(
            select(Collection)
            .where(Collection.store_id == store_id, Collection.is_deleted.is_(False))
            .order_by(Collection.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
