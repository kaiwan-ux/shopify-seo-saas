import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store
from app.repositories.base import BaseRepository


class StoreRepository(BaseRepository[Store]):
    """Repository for Shopify store connections."""

    model = Store

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_owner_id(self, owner_id: uuid.UUID) -> list[Store]:
        result = await self.session.execute(
            select(Store).where(Store.owner_id == owner_id).order_by(Store.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_connected_by_owner_id(self, owner_id: uuid.UUID) -> list[Store]:
        result = await self.session.execute(
            select(Store)
            .where(Store.owner_id == owner_id, Store.is_connected.is_(True))
            .order_by(Store.installed_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_shop_domain(self, shop_domain: str) -> Store | None:
        result = await self.session.execute(
            select(Store).where(Store.shop_domain == shop_domain.lower())
        )
        return result.scalar_one_or_none()
