"""Application service coordinating Phase 4 engines and persistence."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence import (
    ContentIntelligenceEngine,
    MetadataIntelligenceEngine,
    RecommendationEngine,
    RedirectIntelligenceEngine,
    SchemaIntelligenceEngine,
    SEOAuditEngine,
    SEOScoringEngine,
    TechnicalSEOEngine,
)
from app.models.seo import (
    ContentGenerationLog,
    SchemaValidation,
    SEOReport,
    TechnicalAudit,
)
from app.models.seo import (
    RedirectRecommendation as RedirectRecommendationModel,
)
from app.repositories.seo import SEOReportRepository
from app.schemas.seo import (
    AuditRequest,
    ContentRequest,
    RedirectRequest,
    SchemaRequest,
    ScoreRequest,
    TechnicalAuditRequest,
)


class SEOService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.reports = SEOReportRepository(session)
        self.audit_engine = SEOAuditEngine()
        self.technical_engine = TechnicalSEOEngine()
        self.content_engine = ContentIntelligenceEngine()
        self.schema_engine = SchemaIntelligenceEngine()
        self.redirect_engine = RedirectIntelligenceEngine()
        self.scoring_engine = SEOScoringEngine()
        self.metadata_engine = MetadataIntelligenceEngine()
        self.recommendation_engine = RecommendationEngine()

    async def audit(self, request: AuditRequest, store_id: uuid.UUID):
        result = await self.audit_engine.analyze(request)
        recommendations = await self.recommendation_engine.prioritize(result.findings)
        score = await self.scoring_engine.score(ScoreRequest(findings=result.findings))
        report = await self._save_report(
            store_id,
            "audit",
            result.summary,
            result.findings,
            score,
            recommendations,
            result.model_dump(mode="json"),
        )
        return {
            "report_id": report.id,
            **result.model_dump(),
            "score": score,
            "recommendations": recommendations,
        }

    async def technical(self, request: TechnicalAuditRequest, store_id: uuid.UUID):
        result = await self.technical_engine.analyze(request)
        recommendations = await self.recommendation_engine.prioritize(result.findings)
        score = await self.scoring_engine.score(ScoreRequest(findings=result.findings))
        report = await self._save_report(
            store_id,
            "technical",
            result.summary,
            result.findings,
            score,
            recommendations,
            result.model_dump(mode="json"),
        )
        self.session.add(
            TechnicalAudit(
                store_id=store_id,
                report_id=report.id,
                base_url=request.base_url,
                crawled_urls=result.crawled_urls,
                indexable_urls=result.indexable_urls,
                findings=[item.model_dump(mode="json") for item in result.findings],
                summary=result.summary,
                confidence=result.confidence,
            )
        )
        await self.session.flush()
        return {
            "report_id": report.id,
            **result.model_dump(),
            "score": score,
            "recommendations": recommendations,
        }

    async def content(self, request: ContentRequest, store_id: uuid.UUID):
        result = await self.content_engine.generate(request)
        self.session.add(
            ContentGenerationLog(
                store_id=store_id,
                content_type=request.content_type.value,
                prompt_data=request.model_dump(mode="json"),
                generated_content=result.content,
                readability_score=result.readability_score,
                confidence=result.confidence,
            )
        )
        await self.session.flush()
        return result

    async def schema(self, request: SchemaRequest, store_id: uuid.UUID):
        result = await self.schema_engine.generate(request)
        self.session.add(
            SchemaValidation(
                store_id=store_id,
                schema_type=result.schema_type.value,
                json_ld=result.json_ld,
                is_valid=result.valid,
                errors=result.errors,
                warnings=result.warnings,
                confidence=result.confidence,
            )
        )
        await self.session.flush()
        return result

    async def redirect(self, request: RedirectRequest, store_id: uuid.UUID):
        result = await self.redirect_engine.analyze(request)
        self.session.add_all(
            [
                RedirectRecommendationModel(
                    store_id=store_id,
                    source_url=item.source_url,
                    target_url=item.target_url,
                    confidence=item.confidence,
                    reason=item.reason,
                    approval_required=item.approval_required,
                )
                for item in result.recommendations
            ]
        )
        await self.session.flush()
        return result

    async def score(self, request: ScoreRequest):
        return await self.scoring_engine.score(request)

    async def get_report(self, report_id: uuid.UUID, store_id: uuid.UUID):
        report = await self.reports.get_complete(report_id)
        if report is None or report.store_id != store_id:
            return None
        return {
            "id": report.id,
            "store_id": report.store_id,
            "report_type": report.report_type,
            "status": report.status,
            "summary": report.summary,
            "score": report.overall_score,
            "findings": [
                {
                    "code": item.code,
                    "category": item.category,
                    "severity": item.severity,
                    "title": item.title,
                    "explanation": item.explanation,
                    "resource_type": item.resource_type,
                    "resource_id": item.resource_id,
                    "url": item.url,
                    "confidence": item.confidence,
                    "evidence": item.evidence or [],
                    "recommended_action": item.recommended_action,
                    "estimated_impact": item.estimated_impact,
                    "approval_required": item.approval_required,
                }
                for item in report.issues
            ],
            "recommendations": [
                {
                    "priority": item.priority,
                    "issue_code": item.issue_code,
                    "explanation": item.explanation,
                    "estimated_seo_impact": item.estimated_seo_impact,
                    "suggested_fix": item.suggested_fix,
                    "confidence": item.confidence,
                    "approval_required": item.approval_required,
                    "resource_id": item.resource_id,
                }
                for item in report.recommendations
            ],
            "metadata": report.report_data or {},
        }

    async def _save_report(
        self,
        store_id,
        report_type,
        summary,
        findings,
        score,
        recommendations,
        data,
    ):
        report = await self.reports.create(
            SEOReport(
                store_id=store_id,
                report_type=report_type,
                status="completed",
                summary=summary,
                overall_score=score.overall_score,
                report_data=data,
            )
        )
        await self.reports.add_findings(report.id, findings)
        await self.reports.add_scores(report.id, score.category_scores)
        await self.reports.add_recommendations(report.id, recommendations)
        return report
