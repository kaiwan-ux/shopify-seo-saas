import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def upsert(self, store_id: uuid.UUID, shopify_id: str, data: dict[str, Any]) -> Product:
        result = await self.session.execute(
            select(Product).where(Product.store_id == store_id, Product.shopify_id == shopify_id)
        )
        product = result.scalar_one_or_none()

        if product is None:
            product = Product(store_id=store_id, shopify_id=shopify_id, **data)
            return await self.create(product)

        for key, value in data.items():
            setattr(product, key, value)
        await self.session.flush()
        await self.session.refresh(product)
        return product


    async def get_by_store_and_id(self, store_id: uuid.UUID, product_id: uuid.UUID) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.store_id == store_id, Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_store_and_shopify_id(self, store_id: uuid.UUID, shopify_id: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.store_id == store_id, Product.shopify_id == shopify_id)
        )
        return result.scalar_one_or_none()

    async def list_by_store(self, store_id: uuid.UUID, limit: int = 50) -> list[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.store_id == store_id, Product.is_deleted.is_(False))
            .order_by(Product.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_deleted(self, store_id: uuid.UUID, shopify_id: str) -> None:
        await self.session.execute(
            update(Product)
            .where(Product.store_id == store_id, Product.shopify_id == shopify_id)
            .values(is_deleted=True)
        )
        await self.session.flush()
