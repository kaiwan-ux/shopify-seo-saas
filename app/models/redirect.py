"""Synced Shopify URL redirect."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Redirect(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Local mirror of a Shopify URL redirect."""

    __tablename__ = "redirects"
    __table_args__ = (
        UniqueConstraint("store_id", "shopify_id", name="uq_redirects_store_shopify_id"),
    )

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shopify_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    path: Mapped[str] = mapped_column(String(2048), nullable=False)
    target: Mapped[str] = mapped_column(String(2048), nullable=False)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    store: Mapped["Store"] = relationship("Store", back_populates="redirects")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Redirect id={self.id} path={self.path!r}>"
