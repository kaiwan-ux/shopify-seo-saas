"""Provider-neutral keyword extraction, intent, density, and placement analysis."""

from collections import Counter

from app.intelligence.utils import STOP_WORDS, words
from app.schemas.seo import (
    Evidence,
    KeywordAnalysisResult,
    KeywordMetric,
    KeywordRequest,
    ResourceType,
    SearchIntent,
    SEOFinding,
    Severity,
)


class KeywordIntelligenceEngine:
    async def analyze(self, request: KeywordRequest) -> KeywordAnalysisResult:
        tokens = words(request.text)
        counts = Counter(token for token in tokens if len(token) > 2 and token not in STOP_WORDS)
        candidates = [*request.seed_keywords]
        candidates.extend(term for term, _ in counts.most_common(15) if term not in candidates)
        primary = candidates[0] if candidates else None
        secondary = candidates[1:6]
        title_lower = request.title.lower()
        headings = " ".join(request.headings).lower()
        body_lower = request.text.lower()
        metrics: list[KeywordMetric] = []
        findings: list[SEOFinding] = []

        for keyword in candidates[:10]:
            count = body_lower.count(keyword.lower())
            placement = []
            if keyword.lower() in title_lower:
                placement.append("title")
            if keyword.lower() in headings:
                placement.append("headings")
            if keyword.lower() in " ".join(tokens[:100]):
                placement.append("introduction")
            density = round((count * max(1, len(words(keyword))) / max(1, len(tokens))) * 100, 2)
            metrics.append(
                KeywordMetric(keyword=keyword, count=count, density=density, placements=placement)
            )

        if primary:
            metric = metrics[0]
            if metric.density == 0:
                findings.append(
                    self._finding(
                        "keyword.primary_missing",
                        Severity.HIGH,
                        "Primary keyword is absent",
                        "Use the primary topic naturally in the copy.",
                        metric.density,
                        "Present naturally",
                    )
                )
            elif metric.density > 3:
                findings.append(
                    self._finding(
                        "keyword.overuse",
                        Severity.MEDIUM,
                        "Possible keyword overuse",
                        "Reduce repetition and use natural semantic variants.",
                        metric.density,
                        "Generally below 3%",
                    )
                )
            if "title" not in metric.placements:
                findings.append(
                    self._finding(
                        "keyword.title_placement",
                        Severity.MEDIUM,
                        "Primary keyword missing from title",
                        "Include the topic naturally near the beginning of the title.",
                        metric.placements,
                        "title",
                    )
                )

        intent = self._intent(f"{request.title} {request.text}")
        semantic = [term for term, _ in counts.most_common(20) if term not in candidates][:10]
        long_tail = self._long_tail(primary, intent)
        return KeywordAnalysisResult(
            primary_keyword=primary,
            secondary_keywords=secondary,
            semantic_keywords=semantic,
            intent=intent,
            metrics=metrics,
            long_tail_suggestions=long_tail,
            findings=findings,
            confidence=min(0.95, 0.55 + len(tokens) / 1000),
        )

    @staticmethod
    def _intent(text: str) -> SearchIntent:
        value = text.lower()
        if any(term in value for term in ("buy", "price", "shop", "order", "discount")):
            return SearchIntent.TRANSACTIONAL
        if any(term in value for term in ("best", "review", "compare", "versus", "top ")):
            return SearchIntent.COMMERCIAL
        if any(term in value for term in ("login", "official", "contact", "near me")):
            return SearchIntent.NAVIGATIONAL
        return SearchIntent.INFORMATIONAL

    @staticmethod
    def _long_tail(primary: str | None, intent: SearchIntent) -> list[str]:
        if not primary:
            return []
        templates = {
            SearchIntent.TRANSACTIONAL: [
                "buy {k} online",
                "best price for {k}",
                "{k} with fast delivery",
            ],
            SearchIntent.COMMERCIAL: [
                "best {k} for beginners",
                "{k} reviews and comparison",
                "how to choose {k}",
            ],
            SearchIntent.NAVIGATIONAL: [
                "official {k} store",
                "{k} customer support",
                "{k} shop location",
            ],
            SearchIntent.INFORMATIONAL: [
                "how to use {k}",
                "what to know about {k}",
                "{k} guide for beginners",
            ],
        }[intent]
        return [template.format(k=primary) for template in templates]

    @staticmethod
    def _finding(
        code: str,
        severity: Severity,
        title: str,
        action: str,
        observed,
        expected,
    ) -> SEOFinding:
        return SEOFinding(
            code=code,
            category="content_quality",
            severity=severity,
            title=title,
            explanation=title,
            resource_type=ResourceType.PAGE,
            confidence=0.9,
            evidence=[Evidence(source="keyword_analysis", observed=observed, expected=expected)],
            recommended_action=action,
            estimated_impact="medium",
        )
