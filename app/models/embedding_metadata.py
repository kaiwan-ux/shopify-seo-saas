"""Embedding metadata for vector store indexing."""

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class EmbeddingMetadata(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks embeddings stored in Qdrant."""

    __tablename__ = "embedding_metadata"

    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    memory_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memory_entries.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    collection_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    qdrant_point_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<EmbeddingMetadata point={self.qdrant_point_id} collection={self.collection_name}>"
