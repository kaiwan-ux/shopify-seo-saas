"""Fast, database-free coverage for Phase 4 expert rules."""

import pytest

from app.intelligence.audit import SEOAuditEngine
from app.intelligence.keywords import KeywordIntelligenceEngine
from app.intelligence.redirects import RedirectIntelligenceEngine
from app.intelligence.schema import SchemaIntelligenceEngine
from app.intelligence.scoring import SEOScoringEngine
from app.intelligence.technical import TechnicalSEOEngine
from app.schemas.seo import (
    AuditRequest,
    CrawlURL,
    KeywordRequest,
    RedirectRequest,
    RedirectSource,
    ResourceType,
    SchemaRequest,
    SchemaType,
    ScoreRequest,
    SEOResource,
    TechnicalAuditRequest,
)


@pytest.mark.asyncio
async def test_audit_detects_missing_metadata_thin_content_and_alt():
    result = await SEOAuditEngine().analyze(
        AuditRequest(
            resources=[
                SEOResource(
                    id="1",
                    resource_type=ResourceType.PRODUCT,
                    url="/products/boot",
                    title="Boot",
                    body='<h1>Boot</h1><img src="boot.jpg">',
                )
            ]
        )
    )
    codes = {finding.code for finding in result.findings}
    assert {"metadata.title_fallback_short", "metadata.missing_description", "content.thin"} <= codes
    assert "accessibility.missing_alt" in codes


@pytest.mark.asyncio
async def test_technical_detects_loop_and_indexability_conflict():
    result = await TechnicalSEOEngine().analyze(
        TechnicalAuditRequest(
            base_url="https://shop.test",
            robots_txt="User-agent: *\nAllow: /",
            sitemap_urls=["https://shop.test/a"],
            urls=[
                CrawlURL(
                    url="https://shop.test/a", status_code=301, redirect_to="https://shop.test/b"
                ),
                CrawlURL(
                    url="https://shop.test/b", status_code=301, redirect_to="https://shop.test/a"
                ),
                CrawlURL(url="https://shop.test/private", robots_index=False, in_sitemap=True),
            ],
        )
    )
    codes = {finding.code for finding in result.findings}
    assert "redirect.loop" in codes
    assert "indexability.noindex_in_sitemap" in codes


@pytest.mark.asyncio
async def test_keyword_intent_and_provider_extension_point():
    result = await KeywordIntelligenceEngine().analyze(
        KeywordRequest(
            title="Buy hiking boots online",
            text="Buy hiking boots online. Compare hiking boots by fit and durability.",
            seed_keywords=["hiking boots"],
        )
    )
    assert result.primary_keyword == "hiking boots"
    assert result.intent.value == "transactional"
    assert result.provider_data == {}


@pytest.mark.asyncio
async def test_schema_generation_and_validation():
    engine = SchemaIntelligenceEngine()
    result = await engine.generate(
        SchemaRequest(
            schema_type=SchemaType.FAQ,
            data={"questions": [{"question": "What is it?", "answer": "A test."}]},
        )
    )
    valid, errors = engine.validate(result.json_ld)
    assert result.valid is True
    assert valid is True
    assert errors == []


@pytest.mark.asyncio
async def test_redirect_similarity_and_scoring():
    product = SEOResource(
        id="2",
        resource_type=ResourceType.PRODUCT,
        url="/products/red-running-shoe",
        title="Red Running Shoe",
        body="Lightweight road running shoe",
    )
    redirect = await RedirectIntelligenceEngine().analyze(
        RedirectRequest(
            sources=[
                RedirectSource(
                    url="/products/old-red-running-shoe",
                    title="Red Running Shoe",
                    content="Lightweight road shoe",
                    resource_type=ResourceType.PRODUCT,
                )
            ],
            targets=[product],
        )
    )
    assert redirect.recommendations[0].target_url == product.url
    audit = await SEOAuditEngine().analyze(AuditRequest(resources=[product]))
    score = await SEOScoringEngine().score(ScoreRequest(findings=audit.findings))
    assert 0 <= score.overall_score < 100
    assert len(score.category_scores) == 7
