"""Semantic internal-link recommendations and site-structure diagnostics."""

from collections import Counter, defaultdict

from app.intelligence.utils import jaccard, meaningful_terms
from app.schemas.seo import (
    Evidence,
    InternalLinkRequest,
    InternalLinkResult,
    LinkRecommendation,
    ResourceType,
    SEOFinding,
    Severity,
)


class InternalLinkingEngine:
    async def analyze(self, request: InternalLinkRequest) -> InternalLinkResult:
        known_urls = {resource.url for resource in request.resources}
        incoming: Counter[str] = Counter()
        existing: set[tuple[str, str]] = set()
        terms: dict[str, set[str]] = {}
        clusters: dict[str, list[str]] = defaultdict(list)

        for resource in request.resources:
            terms[resource.url] = set(
                meaningful_terms(f"{resource.title} {resource.body} {' '.join(resource.keywords)}")
            )
            cluster = (
                resource.keywords[0]
                if resource.keywords
                else next(iter(terms[resource.url]), resource.resource_type.value)
            )
            clusters[cluster].append(resource.url)
            for link in resource.links:
                if link.internal and link.url in known_urls:
                    incoming[link.url] += 1
                    existing.add((resource.url, link.url))

        recommendations: list[LinkRecommendation] = []
        for source in request.resources:
            scored = []
            for target in request.resources:
                if source.url == target.url or (source.url, target.url) in existing:
                    continue
                score = jaccard(terms[source.url], terms[target.url])
                relationship = self._relationship(source.resource_type, target.resource_type)
                if relationship:
                    score += 0.15
                if score >= 0.15:
                    scored.append((score, target, relationship or "semantically_related"))
            for score, target, relationship in sorted(scored, reverse=True, key=lambda row: row[0])[
                :3
            ]:
                recommendations.append(
                    LinkRecommendation(
                        source_url=source.url,
                        target_url=target.url,
                        anchor_text=target.title,
                        relationship=relationship,
                        reason="The resources share a topic and this link improves discovery and user progression.",
                        confidence=min(0.98, round(0.55 + score, 2)),
                    )
                )

        orphan_urls = [
            resource.url for resource in request.resources if incoming[resource.url] == 0
        ]
        findings = [
            SEOFinding(
                code="links.orphan",
                category="internal_linking",
                severity=Severity.HIGH,
                title="Orphan page",
                explanation="No analyzed internal page links to this URL.",
                resource_type=ResourceType.URL,
                url=url,
                confidence=0.92,
                evidence=[
                    Evidence(
                        source="link_graph", observed=0, expected="At least one contextual link"
                    )
                ],
                recommended_action="Add a relevant contextual link from a hub, guide, collection, or related product.",
                estimated_impact="high",
            )
            for url in orphan_urls
        ]
        return InternalLinkResult(
            recommendations=recommendations,
            orphan_urls=orphan_urls,
            distribution={resource.url: incoming[resource.url] for resource in request.resources},
            topic_clusters=dict(clusters),
            findings=findings,
        )

    @staticmethod
    def _relationship(source: ResourceType, target: ResourceType) -> str | None:
        return {
            (ResourceType.BLOG, ResourceType.PRODUCT): "blog_to_product",
            (ResourceType.PRODUCT, ResourceType.BLOG): "product_to_guide",
            (ResourceType.PRODUCT, ResourceType.PRODUCT): "related_product",
            (ResourceType.COLLECTION, ResourceType.COLLECTION): "related_collection",
            (ResourceType.COLLECTION, ResourceType.PRODUCT): "collection_to_product",
        }.get((source, target))
