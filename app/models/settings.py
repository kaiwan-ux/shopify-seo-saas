import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AppSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Per-user application settings."""

    __tablename__ = "app_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    notification_email: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="settings")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AppSettings id={self.id} user_id={self.user_id}>"
