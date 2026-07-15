"""Knowledge base document tracking for RAG."""

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class DocumentSource(StrEnum):
    GOOGLE_SEO = "google_seo"
    SHOPIFY_DOCS = "shopify_docs"
    SCHEMA_ORG = "schema_org"
    INTERNAL = "internal"
    AUDIT_REPORT = "audit_report"
    USER_UPLOAD = "user_upload"


class KnowledgeDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Indexed knowledge document for RAG retrieval."""

    __tablename__ = "knowledge_documents"

    store_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    collection_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_indexed: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<KnowledgeDocument title={self.title!r} source={self.source}>"
