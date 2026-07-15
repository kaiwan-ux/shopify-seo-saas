"""Phase 4 SEO intelligence persistence models."""

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class SEOReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "seo_reports"
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), index=True
    )
    report_type: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    summary: Mapped[str | None] = mapped_column(Text)
    overall_score: Mapped[float | None] = mapped_column(Float)
    report_data: Mapped[dict | None] = mapped_column(JSONB)
    issues: Mapped[list["SEOIssue"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )
    scores: Mapped[list["SEOScore"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class SEOIssue(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "seo_issues"
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seo_reports.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(128), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    title: Mapped[str] = mapped_column(String(512))
    explanation: Mapped[str] = mapped_column(Text)
    resource_type: Mapped[str | None] = mapped_column(String(32))
    resource_id: Mapped[str | None] = mapped_column(String(128), index=True)
    url: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    evidence: Mapped[list | None] = mapped_column(JSONB)
    recommended_action: Mapped[str] = mapped_column(Text)
    estimated_impact: Mapped[str] = mapped_column(String(32))
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    report: Mapped["SEOReport"] = relationship(back_populates="issues")


class SEOScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "seo_scores"
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seo_reports.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str] = mapped_column(String(64), index=True)
    score: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    issue_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float)
    report: Mapped["SEOReport"] = relationship(back_populates="scores")


class Recommendation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "seo_recommendations"
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seo_reports.id", ondelete="CASCADE"), index=True
    )
    issue_code: Mapped[str] = mapped_column(String(128), index=True)
    priority: Mapped[str] = mapped_column(String(16), index=True)
    explanation: Mapped[str] = mapped_column(Text)
    estimated_seo_impact: Mapped[str] = mapped_column(String(32))
    suggested_fix: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    resource_id: Mapped[str | None] = mapped_column(String(128))
    report: Mapped["SEOReport"] = relationship(back_populates="recommendations")


class KeywordAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "keyword_analyses"
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), index=True
    )
    resource_id: Mapped[str | None] = mapped_column(String(128), index=True)
    primary_keyword: Mapped[str | None] = mapped_column(String(512))
    search_intent: Mapped[str] = mapped_column(String(32))
    secondary_keywords: Mapped[list | None] = mapped_column(JSONB)
    semantic_keywords: Mapped[list | None] = mapped_column(JSONB)
    metrics: Mapped[list | None] = mapped_column(JSONB)
    suggestions: Mapped[list | None] = mapped_column(JSONB)
    confidence: Mapped[float] = mapped_column(Float)
    provider_data: Mapped[dict | None] = mapped_column(JSONB)


class SchemaValidation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "schema_validations"
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), index=True
    )
    resource_id: Mapped[str | None] = mapped_column(String(128), index=True)
    schema_type: Mapped[str] = mapped_column(String(64))
    json_ld: Mapped[dict] = mapped_column(JSONB)
    is_valid: Mapped[bool] = mapped_column(Boolean)
    errors: Mapped[list | None] = mapped_column(JSONB)
    warnings: Mapped[list | None] = mapped_column(JSONB)
    confidence: Mapped[float] = mapped_column(Float)


class RedirectRecommendation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "redirect_recommendations"
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), index=True
    )
    source_url: Mapped[str] = mapped_column(Text)
    target_url: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True)


class ContentGenerationLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "content_generation_logs"
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), index=True
    )
    resource_id: Mapped[str | None] = mapped_column(String(128), index=True)
    content_type: Mapped[str] = mapped_column(String(64))
    prompt_data: Mapped[dict | None] = mapped_column(JSONB)
    generated_content: Mapped[str] = mapped_column(Text)
    readability_score: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)


class TechnicalAudit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "technical_audits"
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), index=True
    )
    report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seo_reports.id", ondelete="SET NULL"), index=True
    )
    base_url: Mapped[str] = mapped_column(Text)
    crawled_urls: Mapped[int] = mapped_column(Integer)
    indexable_urls: Mapped[int] = mapped_column(Integer)
    findings: Mapped[list | None] = mapped_column(JSONB)
    summary: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
