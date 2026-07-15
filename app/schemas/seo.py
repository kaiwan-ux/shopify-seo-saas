"""Typed contracts shared by every Phase 4 SEO intelligence module."""

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResourceType(StrEnum):
    PRODUCT = "product"
    COLLECTION = "collection"
    BLOG = "blog"
    PAGE = "page"
    IMAGE = "image"
    URL = "url"
    STORE = "store"


class SearchIntent(StrEnum):
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


class Evidence(BaseModel):
    source: str
    observed: Any = None
    expected: Any = None
    url: str | None = None


class SEOFinding(BaseModel):
    code: str
    category: str
    severity: Severity
    title: str
    explanation: str
    resource_type: ResourceType = ResourceType.URL
    resource_id: str | None = None
    url: str | None = None
    confidence: float = Field(default=0.9, ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)
    recommended_action: str
    estimated_impact: str = "medium"
    approval_required: bool = False


class ImageInput(BaseModel):
    url: str
    alt: str | None = None


class LinkInput(BaseModel):
    url: str
    status_code: int | None = None
    anchor_text: str | None = None
    internal: bool = True


class SEOResource(BaseModel):
    id: str
    resource_type: ResourceType
    url: str
    title: str
    body: str = ""
    seo_title: str | None = None
    meta_description: str | None = None
    canonical_url: str | None = None
    headings: list[str] = Field(default_factory=list)
    images: list[ImageInput] = Field(default_factory=list)
    links: list[LinkInput] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    published: bool = True
    indexable: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditRequest(BaseModel):
    store_id: UUID | None = None
    resources: list[SEOResource] = Field(default_factory=list, max_length=5000)


class AuditResult(BaseModel):
    findings: list[SEOFinding]
    resources_analyzed: int
    summary: str
    confidence: float = Field(ge=0, le=1)


class CrawlURL(BaseModel):
    url: str
    status_code: int = 200
    canonical_url: str | None = None
    redirect_to: str | None = None
    robots_index: bool = True
    robots_follow: bool = True
    in_sitemap: bool = True
    hreflang: dict[str, str] = Field(default_factory=dict)
    breadcrumbs: list[str] = Field(default_factory=list)
    pagination_next: str | None = None
    pagination_prev: str | None = None
    internal_links: list[str] = Field(default_factory=list)


class TechnicalAuditRequest(BaseModel):
    store_id: UUID | None = None
    base_url: str
    robots_txt: str | None = None
    sitemap_urls: list[str] = Field(default_factory=list)
    urls: list[CrawlURL] = Field(default_factory=list, max_length=10000)


class TechnicalAuditResult(BaseModel):
    findings: list[SEOFinding]
    crawled_urls: int
    indexable_urls: int
    summary: str
    confidence: float = Field(ge=0, le=1)


class MetadataRequest(BaseModel):
    resource: SEOResource
    brand_name: str | None = None
    primary_keyword: str | None = None
    site_url: str | None = None


class MetadataResult(BaseModel):
    seo_title: str
    meta_description: str
    open_graph: dict[str, str]
    twitter_card: dict[str, str]
    canonical_tag: str
    rich_snippet: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class KeywordRequest(BaseModel):
    text: str
    title: str = ""
    headings: list[str] = Field(default_factory=list)
    seed_keywords: list[str] = Field(default_factory=list)


class KeywordMetric(BaseModel):
    keyword: str
    count: int
    density: float
    placements: list[str] = Field(default_factory=list)


class KeywordAnalysisResult(BaseModel):
    primary_keyword: str | None
    secondary_keywords: list[str]
    semantic_keywords: list[str]
    intent: SearchIntent
    metrics: list[KeywordMetric]
    long_tail_suggestions: list[str]
    findings: list[SEOFinding] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    provider_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Reserved for Search Console and third-party keyword metrics.",
    )


class InternalLinkRequest(BaseModel):
    resources: list[SEOResource] = Field(default_factory=list, max_length=5000)


class LinkRecommendation(BaseModel):
    source_url: str
    target_url: str
    anchor_text: str
    relationship: str
    reason: str
    confidence: float = Field(ge=0, le=1)


class InternalLinkResult(BaseModel):
    recommendations: list[LinkRecommendation]
    orphan_urls: list[str]
    distribution: dict[str, int]
    topic_clusters: dict[str, list[str]]
    findings: list[SEOFinding]


class SchemaType(StrEnum):
    PRODUCT = "Product"
    ORGANIZATION = "Organization"
    FAQ = "FAQPage"
    REVIEW = "Review"
    BREADCRUMB = "BreadcrumbList"
    ARTICLE = "Article"
    COLLECTION = "CollectionPage"
    VIDEO = "VideoObject"
    LOCAL_BUSINESS = "LocalBusiness"


class SchemaRequest(BaseModel):
    schema_type: SchemaType
    data: dict[str, Any]


class SchemaResult(BaseModel):
    schema_type: SchemaType
    json_ld: dict[str, Any]
    valid: bool
    errors: list[str]
    warnings: list[str]
    confidence: float = Field(ge=0, le=1)


class RedirectSource(BaseModel):
    url: str
    title: str = ""
    content: str = ""
    resource_type: ResourceType = ResourceType.URL


class RedirectRequest(BaseModel):
    store_id: UUID | None = None
    sources: list[RedirectSource] = Field(default_factory=list)
    targets: list[SEOResource] = Field(default_factory=list)
    existing_redirects: dict[str, str] = Field(default_factory=dict)


class RedirectSuggestion(BaseModel):
    source_url: str
    target_url: str | None
    confidence: float = Field(ge=0, le=1)
    reason: str
    approval_required: bool = True


class RedirectResult(BaseModel):
    recommendations: list[RedirectSuggestion]
    loops: list[list[str]]
    chains: list[list[str]]
    findings: list[SEOFinding]


class ContentType(StrEnum):
    PRODUCT_DESCRIPTION = "product_description"
    COLLECTION_DESCRIPTION = "collection_description"
    FAQ = "faq"
    BUYING_GUIDE = "buying_guide"
    COMPARISON = "comparison"
    PROS_CONS = "pros_cons"
    FEATURE_HIGHLIGHTS = "feature_highlights"
    ALT_TEXT = "alt_text"


class ContentRequest(BaseModel):
    content_type: ContentType
    topic: str = Field(min_length=1, max_length=500)
    primary_keyword: str = Field(min_length=1, max_length=200)
    secondary_keywords: list[str] = Field(default_factory=list, max_length=20)
    attributes: dict[str, Any] = Field(default_factory=dict)
    tone: str = "clear, helpful, and trustworthy"
    target_words: int = Field(default=300, ge=20, le=3000)


class ContentResult(BaseModel):
    content_type: ContentType
    content: str
    title: str | None = None
    sections: list[dict[str, str]] = Field(default_factory=list)
    keywords_used: list[str]
    readability_score: float = Field(ge=0, le=100)
    intent: SearchIntent
    confidence: float = Field(ge=0, le=1)
    requires_human_review: bool = True


DEFAULT_SCORE_WEIGHTS = {
    "metadata": 0.20,
    "technical": 0.20,
    "content_quality": 0.20,
    "internal_linking": 0.10,
    "schema": 0.10,
    "performance": 0.10,
    "accessibility": 0.10,
}


class ScoreRequest(BaseModel):
    findings: list[SEOFinding] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    weights: dict[str, float] = Field(default_factory=lambda: DEFAULT_SCORE_WEIGHTS.copy())

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, value: dict[str, float]) -> dict[str, float]:
        if not value or any(weight < 0 for weight in value.values()):
            raise ValueError("weights must be non-negative and non-empty")
        if sum(value.values()) <= 0:
            raise ValueError("at least one weight must be positive")
        return value


class CategoryScore(BaseModel):
    category: str
    score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0)
    issue_count: int
    confidence: float = Field(ge=0, le=1)


class ScoreResult(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    category_scores: list[CategoryScore]
    issue_severity: dict[Severity, int]
    confidence: float = Field(ge=0, le=1)


class Recommendation(BaseModel):
    priority: Severity
    issue_code: str
    explanation: str
    estimated_seo_impact: str
    suggested_fix: str
    confidence: float = Field(ge=0, le=1)
    approval_required: bool
    resource_id: str | None = None


class SEOReportResponse(BaseModel):
    id: UUID
    store_id: UUID
    report_type: str
    status: str
    summary: str | None = None
    score: float | None = None
    findings: list[SEOFinding] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
