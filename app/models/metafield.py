"""Synced Shopify metafield."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Metafield(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Local mirror of a Shopify metafield."""

    __tablename__ = "metafields"
    __table_args__ = (
        UniqueConstraint("store_id", "shopify_id", name="uq_metafields_store_shopify_id"),
    )

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    shopify_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_shopify_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    product: Mapped["Product | None"] = relationship("Product", back_populates="metafields")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Metafield id={self.id} {self.namespace}.{self.key}>"
