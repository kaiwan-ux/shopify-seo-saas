import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blog import Blog
from app.repositories.base import BaseRepository


class BlogRepository(BaseRepository[Blog]):
    model = Blog

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def upsert(self, store_id: uuid.UUID, shopify_id: str, data: dict[str, Any]) -> Blog:
        result = await self.session.execute(
            select(Blog).where(Blog.store_id == store_id, Blog.shopify_id == shopify_id)
        )
        entity = result.scalar_one_or_none()
        if entity is None:
            entity = Blog(store_id=store_id, shopify_id=shopify_id, **data)
            return await self.create(entity)
        for key, value in data.items():
            setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
