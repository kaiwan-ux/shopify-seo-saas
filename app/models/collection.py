"""Synced Shopify collection."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Collection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Local mirror of a Shopify collection."""

    __tablename__ = "collections"
    __table_args__ = (
        UniqueConstraint("store_id", "shopify_id", name="uq_collections_store_shopify_id"),
    )

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shopify_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    handle: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    collection_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    seo_title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    products_count: Mapped[int | None] = mapped_column(nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    store: Mapped["Store"] = relationship("Store", back_populates="collections")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Collection id={self.id} shopify_id={self.shopify_id} handle={self.handle!r}>"
