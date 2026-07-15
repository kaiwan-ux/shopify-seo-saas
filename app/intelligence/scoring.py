"""Configurable, category-based SEO scoring."""

from collections import Counter, defaultdict

from app.schemas.seo import CategoryScore, ScoreRequest, ScoreResult, Severity

PENALTIES = {
    Severity.CRITICAL: 30,
    Severity.HIGH: 18,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
}


class SEOScoringEngine:
    async def score(self, request: ScoreRequest) -> ScoreResult:
        total_weight = sum(request.weights.values())
        weights = {key: value / total_weight for key, value in request.weights.items()}
        by_category = defaultdict(list)
        for finding in request.findings:
            by_category[finding.category].append(finding)

        category_scores = []
        for category, weight in weights.items():
            issues = by_category[category]
            base = request.metrics.get(category, 100.0)
            penalty = sum(PENALTIES[issue.severity] * issue.confidence for issue in issues)
            score = round(max(0, min(100, base - penalty)), 1)
            confidence = (
                round(sum(item.confidence for item in issues) / len(issues), 2)
                if issues
                else (0.9 if category in request.metrics else 0.65)
            )
            category_scores.append(
                CategoryScore(
                    category=category,
                    score=score,
                    weight=weight,
                    issue_count=len(issues),
                    confidence=confidence,
                )
            )
        overall = round(sum(item.score * item.weight for item in category_scores), 1)
        severity = Counter(item.severity for item in request.findings)
        confidence = round(sum(item.confidence * item.weight for item in category_scores), 2)
        return ScoreResult(
            overall_score=overall,
            category_scores=category_scores,
            issue_severity={level: severity[level] for level in Severity},
            confidence=confidence,
        )
