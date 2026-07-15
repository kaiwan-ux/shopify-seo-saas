"""Shopify store connected via OAuth."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class SyncStatus(StrEnum):
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"


class Store(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Shopify store connected via Partner App OAuth."""

    __tablename__ = "stores"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    shop_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shopify_shop_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    encrypted_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sync_status: Mapped[str] = mapped_column(String(32), default=SyncStatus.IDLE, nullable=False)
    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    uninstalled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped["User"] = relationship("User", back_populates="stores")  # noqa: F821
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        "Product", back_populates="store", cascade="all, delete-orphan"
    )
    collections: Mapped[list["Collection"]] = relationship(  # noqa: F821
        "Collection", back_populates="store", cascade="all, delete-orphan"
    )
    pages: Mapped[list["Page"]] = relationship(  # noqa: F821
        "Page", back_populates="store", cascade="all, delete-orphan"
    )
    blogs: Mapped[list["Blog"]] = relationship(  # noqa: F821
        "Blog", back_populates="store", cascade="all, delete-orphan"
    )
    redirects: Mapped[list["Redirect"]] = relationship(  # noqa: F821
        "Redirect", back_populates="store", cascade="all, delete-orphan"
    )
    sync_logs: Mapped[list["SyncLog"]] = relationship(  # noqa: F821
        "SyncLog", back_populates="store", cascade="all, delete-orphan"
    )
    webhook_logs: Mapped[list["WebhookLog"]] = relationship(  # noqa: F821
        "WebhookLog", back_populates="store", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Store id={self.id} domain={self.shop_domain!r} connected={self.is_connected}>"
