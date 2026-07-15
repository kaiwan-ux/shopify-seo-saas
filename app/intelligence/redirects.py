"""Redirect target matching plus chain and loop detection."""

from difflib import SequenceMatcher

from app.intelligence.utils import jaccard, meaningful_terms
from app.schemas.seo import (
    Evidence,
    RedirectRequest,
    RedirectResult,
    RedirectSuggestion,
    ResourceType,
    SEOFinding,
    Severity,
)


class RedirectIntelligenceEngine:
    async def analyze(self, request: RedirectRequest) -> RedirectResult:
        recommendations = []
        for source in request.sources:
            best_target = None
            best_score = 0.0
            source_terms = set(meaningful_terms(f"{source.title} {source.content} {source.url}"))
            for target in request.targets:
                target_terms = set(meaningful_terms(f"{target.title} {target.body} {target.url}"))
                semantic = jaccard(source_terms, target_terms)
                lexical = SequenceMatcher(None, source.url.lower(), target.url.lower()).ratio()
                same_type = 0.1 if source.resource_type == target.resource_type else 0
                score = 0.6 * semantic + 0.3 * lexical + same_type
                if score > best_score:
                    best_score, best_target = score, target
            confidence = min(0.99, round(best_score, 2))
            recommendations.append(
                RedirectSuggestion(
                    source_url=source.url,
                    target_url=best_target.url if best_target and confidence >= 0.25 else None,
                    confidence=confidence,
                    reason=(
                        "Best available target based on topic, URL, and resource-type similarity."
                        if best_target and confidence >= 0.25
                        else "No sufficiently relevant target; preserve a useful 404 rather than redirecting arbitrarily."
                    ),
                )
            )

        loops: list[list[str]] = []
        chains: list[list[str]] = []
        for start in request.existing_redirects:
            path, seen, current = [start], {start}, start
            while current in request.existing_redirects:
                current = request.existing_redirects[current]
                path.append(current)
                if current in seen:
                    loops.append(path)
                    break
                seen.add(current)
            if len(path) > 2 and path not in loops:
                chains.append(path)

        findings = []
        for path in loops:
            findings.append(
                self._finding(
                    "redirect.loop",
                    Severity.CRITICAL,
                    path[0],
                    f"Redirect loop: {' → '.join(path)}",
                    "Point every source directly to one valid final destination.",
                )
            )
        for path in chains:
            findings.append(
                self._finding(
                    "redirect.chain",
                    Severity.HIGH,
                    path[0],
                    f"Redirect chain has {len(path) - 1} hops.",
                    "Collapse the chain into a single redirect to the final destination.",
                )
            )
        return RedirectResult(
            recommendations=recommendations, loops=loops, chains=chains, findings=findings
        )

    @staticmethod
    def _finding(
        code: str,
        severity: Severity,
        url: str,
        explanation: str,
        action: str,
    ) -> SEOFinding:
        return SEOFinding(
            code=code,
            category="technical",
            severity=severity,
            title=code.replace(".", " ").title(),
            explanation=explanation,
            resource_type=ResourceType.URL,
            url=url,
            confidence=0.99,
            evidence=[Evidence(source="redirect_graph", url=url)],
            recommended_action=action,
            estimated_impact="high",
            approval_required=True,
        )
