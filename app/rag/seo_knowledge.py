"""Curated Phase 4 knowledge sources for Qdrant indexing.

The seed summaries make a fresh environment useful immediately. Production
ingestion can replace each summary with the licensed/current source document
while preserving source IDs and retrieval filters.
"""

from dataclasses import dataclass

from app.rag.loader import load_text_content
from app.rag.pipeline import RAGPipeline


@dataclass(frozen=True)
class SEOKnowledgeSource:
    source_id: str
    title: str
    url: str
    summary: str


SEO_KNOWLEDGE_SOURCES = (
    SEOKnowledgeSource(
        "google_search_essentials",
        "Google Search Essentials",
        "https://developers.google.com/search/docs/essentials",
        "Create helpful, reliable, people-first content; make links crawlable; use words "
        "people search for in prominent locations; do not use spam techniques.",
    ),
    SEOKnowledgeSource(
        "google_quality_raters",
        "Google Search Quality Rater Guidelines",
        "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf",
        "Evaluate page purpose, main-content quality, reputation, experience, expertise, "
        "authoritativeness, trust, and whether results satisfy likely user needs.",
    ),
    SEOKnowledgeSource(
        "shopify_seo",
        "Shopify SEO documentation",
        "https://help.shopify.com/en/manual/promoting-marketing/seo",
        "Shopify stores expose editable titles and descriptions, canonical tags, sitemap.xml, "
        "robots.txt, redirects, image ALT text, and structured product data.",
    ),
    SEOKnowledgeSource(
        "schema_org",
        "Schema.org vocabulary",
        "https://schema.org/docs/schemas.html",
        "JSON-LD entities must use recognized types and properties. Product, Offer, Article, "
        "BreadcrumbList, FAQPage, Organization, Review and LocalBusiness require type-specific data.",
    ),
    SEOKnowledgeSource(
        "core_web_vitals",
        "Core Web Vitals documentation",
        "https://web.dev/articles/vitals",
        "User experience is measured through loading responsiveness and visual stability, "
        "including LCP, INP, and CLS field performance.",
    ),
    SEOKnowledgeSource(
        "google_rich_results",
        "Google structured data and rich results",
        "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data",
        "Structured data must describe visible page content, follow feature policies, use "
        "supported properties, and remain technically valid without guaranteeing a rich result.",
    ),
    SEOKnowledgeSource(
        "internal_best_practices",
        "Internal Shopify SEO best practices",
        "internal://seo-best-practices",
        "Prefer unique intent-aligned pages, descriptive internal anchors, shallow discovery "
        "paths, one-hop redirects, accessible images, evidence-backed recommendations, and review "
        "before any storefront mutation.",
    ),
)


async def index_seo_knowledge(pipeline: RAGPipeline) -> dict[str, int]:
    """Index all curated sources into the existing Qdrant knowledge collection."""
    await pipeline.initialize()
    indexed = 0
    for source in SEO_KNOWLEDGE_SOURCES:
        result = await pipeline.index_document(
            load_text_content(
                title=source.title,
                content=source.summary,
                source=source.source_id,
                metadata={"url": source.url, "domain": "seo", "phase": 4},
            )
        )
        indexed += int(result["indexed"])
    return {"sources": len(SEO_KNOWLEDGE_SOURCES), "chunks": indexed}
