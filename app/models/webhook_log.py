"""Webhook processing audit log."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class WebhookLogStatus(StrEnum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class WebhookLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log for incoming Shopify webhooks."""

    __tablename__ = "webhook_logs"

    store_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True
    )
    topic: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    shop_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    shopify_webhook_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=WebhookLogStatus.RECEIVED, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    store: Mapped["Store | None"] = relationship("Store", back_populates="webhook_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<WebhookLog id={self.id} topic={self.topic} status={self.status}>"
