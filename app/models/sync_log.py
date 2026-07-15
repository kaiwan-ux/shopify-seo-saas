"""Synchronization audit log."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class SyncType(StrEnum):
    FULL = "full"
    PRODUCTS = "products"
    COLLECTIONS = "collections"
    PAGES = "pages"
    BLOGS = "blogs"
    REDIRECTS = "redirects"


class SyncLogStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log for store synchronization jobs."""

    __tablename__ = "sync_logs"

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sync_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=SyncLogStatus.PENDING, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    store: Mapped["Store"] = relationship("Store", back_populates="sync_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<SyncLog id={self.id} type={self.sync_type} status={self.status}>"
