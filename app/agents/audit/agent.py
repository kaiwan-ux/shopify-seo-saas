"""SEO Audit Agent — consumes the reusable Phase 4 audit engine."""

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction
from app.intelligence.adapters import resources_from_store_data
from app.intelligence.audit import SEOAuditEngine
from app.intelligence.recommendations import RecommendationEngine
from app.intelligence.scoring import SEOScoringEngine
from app.schemas.seo import AuditRequest, ScoreRequest


class AuditAgent(BaseAgent):
    name = AgentName.AUDIT

    async def _execute(self, context: AgentContext) -> AgentOutput:
        store_data = context.store_data or await self._fetch_store_data(context.store_id)
        result = await SEOAuditEngine().analyze(
            AuditRequest(store_id=context.store_id, resources=resources_from_store_data(store_data))
        )
        score = await SEOScoringEngine().score(ScoreRequest(findings=result.findings))
        recommendations = await RecommendationEngine().prioritize(result.findings)
        payload = result.model_dump(mode="json")
        payload["overall_score"] = score.overall_score
        payload["category_scores"] = [
            item.model_dump(mode="json") for item in score.category_scores
        ]
        payload["recommendations"] = [item.model_dump(mode="json") for item in recommendations]
        return AgentOutput(
            agent_name=self.name,
            reasoning=result.summary,
            result=payload,
            confidence=result.confidence,
            next_action=NextAction.CONTINUE,
            required_tools=["get_products", "get_collections", "get_pages"],
        )
