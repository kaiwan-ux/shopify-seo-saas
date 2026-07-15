"""Reporting Agent — aggregates structured Phase 4 intelligence outputs."""

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction
from app.intelligence.recommendations import RecommendationEngine
from app.intelligence.scoring import SEOScoringEngine
from app.schemas.seo import ScoreRequest, SEOFinding


class ReportingAgent(BaseAgent):
    name = AgentName.REPORTING

    async def _execute(self, context: AgentContext) -> AgentOutput:
        findings = []
        for output in context.agent_outputs.values():
            for raw in output.result.get("findings", output.result.get("issues", [])):
                try:
                    findings.append(SEOFinding.model_validate(raw))
                except (TypeError, ValueError):
                    continue
        score = await SEOScoringEngine().score(ScoreRequest(findings=findings))
        recommendations = await RecommendationEngine().prioritize(findings)
        result = {
            "executive_summary": f"SEO score {score.overall_score}/100 with {len(findings)} prioritized issues.",
            "overall_score": score.overall_score,
            "category_scores": [item.model_dump(mode="json") for item in score.category_scores],
            "issue_severity": {key.value: value for key, value in score.issue_severity.items()},
            "recommendations": [item.model_dump(mode="json") for item in recommendations],
            "confidence": score.confidence,
        }
        return AgentOutput(
            agent_name=self.name,
            reasoning=result["executive_summary"],
            result=result,
            confidence=score.confidence,
            next_action=NextAction.CONTINUE,
        )
