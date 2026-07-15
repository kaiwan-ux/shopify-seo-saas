"""Persistence operations for complete SEO reports."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.seo import Recommendation, SEOIssue, SEOReport, SEOScore
from app.repositories.base import BaseRepository
from app.schemas.seo import CategoryScore, SEOFinding
from app.schemas.seo import Recommendation as RecommendationSchema


class SEOReportRepository(BaseRepository[SEOReport]):
    model = SEOReport

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_complete(self, report_id: uuid.UUID) -> SEOReport | None:
        result = await self.session.execute(
            select(SEOReport)
            .options(
                selectinload(SEOReport.issues),
                selectinload(SEOReport.scores),
                selectinload(SEOReport.recommendations),
            )
            .where(SEOReport.id == report_id)
        )
        return result.scalar_one_or_none()

    async def add_findings(self, report_id: uuid.UUID, findings: list[SEOFinding]) -> None:
        self.session.add_all(
            [
                SEOIssue(
                    report_id=report_id,
                    code=item.code,
                    category=item.category,
                    severity=item.severity.value,
                    title=item.title,
                    explanation=item.explanation,
                    resource_type=item.resource_type.value,
                    resource_id=item.resource_id,
                    url=item.url,
                    confidence=item.confidence,
                    evidence=[value.model_dump(mode="json") for value in item.evidence],
                    recommended_action=item.recommended_action,
                    estimated_impact=item.estimated_impact,
                    approval_required=item.approval_required,
                )
                for item in findings
            ]
        )
        await self.session.flush()

    async def add_scores(self, report_id: uuid.UUID, scores: list[CategoryScore]) -> None:
        self.session.add_all(
            [SEOScore(report_id=report_id, **item.model_dump()) for item in scores]
        )
        await self.session.flush()

    async def add_recommendations(
        self,
        report_id: uuid.UUID,
        recommendations: list[RecommendationSchema],
    ) -> None:
        self.session.add_all(
            [
                Recommendation(
                    report_id=report_id,
                    **item.model_dump(mode="json", exclude={"priority"}),
                    priority=item.priority.value,
                )
                for item in recommendations
            ]
        )
        await self.session.flush()
