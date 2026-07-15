"""Semantic memory entries for agents and users."""

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class MemoryType(StrEnum):
    CONVERSATION = "conversation"
    WORKFLOW = "workflow"
    AGENT = "agent"
    STORE = "store"
    USER_PREFERENCE = "user_preference"
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"


class MemoryEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Persistent memory entry with optional Qdrant vector reference."""

    __tablename__ = "memory_entries"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    store_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True
    )
    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    memory_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    qdrant_point_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    collection_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    def __repr__(self) -> str:
        return f"<MemoryEntry type={self.memory_type} key={self.key!r}>"
