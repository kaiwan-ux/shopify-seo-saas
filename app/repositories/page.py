import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.page import Page
from app.repositories.base import BaseRepository


class PageRepository(BaseRepository[Page]):
    model = Page

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def upsert(self, store_id: uuid.UUID, shopify_id: str, data: dict[str, Any]) -> Page:
        result = await self.session.execute(
            select(Page).where(Page.store_id == store_id, Page.shopify_id == shopify_id)
        )
        entity = result.scalar_one_or_none()
        if entity is None:
            entity = Page(store_id=store_id, shopify_id=shopify_id, **data)
            return await self.create(entity)
        for key, value in data.items():
            setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity



    async def get_by_store_and_id(self, store_id: uuid.UUID, entity_id: uuid.UUID) -> Page | None:
        result = await self.session.execute(
            select(Page).where(Page.store_id == store_id, Page.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_store_and_shopify_id(self, store_id: uuid.UUID, shopify_id: str) -> Page | None:
        result = await self.session.execute(
            select(Page).where(Page.store_id == store_id, Page.shopify_id == shopify_id)
        )
        return result.scalar_one_or_none()

    async def list_by_store(self, store_id: uuid.UUID, limit: int = 50) -> list[Page]:
        result = await self.session.execute(
            select(Page)
            .where(Page.store_id == store_id, Page.is_deleted.is_(False))
            .order_by(Page.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
