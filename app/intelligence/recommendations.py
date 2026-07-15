"""Convert findings into consistently prioritized, actionable recommendations."""

from app.schemas.seo import Recommendation, SEOFinding


class RecommendationEngine:
    async def prioritize(self, findings: list[SEOFinding]) -> list[Recommendation]:
        recommendations = [
            Recommendation(
                priority=finding.severity,
                issue_code=finding.code,
                explanation=finding.explanation,
                estimated_seo_impact=finding.estimated_impact,
                suggested_fix=finding.recommended_action,
                confidence=finding.confidence,
                approval_required=finding.approval_required,
                resource_id=finding.resource_id,
            )
            for finding in findings
        ]
        rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(
            recommendations,
            key=lambda item: (rank[item.priority.value], -item.confidence),
        )
