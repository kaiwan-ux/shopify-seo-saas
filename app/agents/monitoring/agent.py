"""Monitoring Agent — detect regressions and summarize current SEO health."""

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction
from app.intelligence.adapters import resources_from_store_data
from app.intelligence.audit import SEOAuditEngine
from app.intelligence.scoring import SEOScoringEngine
from app.schemas.seo import AuditRequest, ScoreRequest


class MonitoringAgent(BaseAgent):
    name = AgentName.MONITORING

    async def _execute(self, context: AgentContext) -> AgentOutput:
        audit_output = context.agent_outputs.get("audit")

        if audit_output and isinstance(audit_output.result, dict) and audit_output.result.get("findings") is not None:
            current = audit_output.result
            findings = current.get("findings", [])
            score = current.get("overall_score")
            resources_analyzed = current.get("resources_analyzed", 0)
        else:
            store_data = context.store_data or await self._fetch_store_data(context.store_id)
            audit = await SEOAuditEngine().analyze(
                AuditRequest(store_id=context.store_id, resources=resources_from_store_data(store_data))
            )
            scored = await SEOScoringEngine().score(ScoreRequest(findings=audit.findings))
            findings = [item.model_dump(mode="json") for item in audit.findings]
            score = scored.overall_score
            resources_analyzed = audit.resources_analyzed
            current = {
                "summary": audit.summary,
                "resources_analyzed": resources_analyzed,
                "findings": findings,
                "overall_score": score,
                "issue_severity": {key.value: value for key, value in scored.issue_severity.items()},
            }

        historical = await self.rag.retrieve_memory(
            f"audit store {context.store_id}", memory_type="workflow"
        )
        regression_count = 0
        improved = False
        previous_score = None

        for item in historical or []:
            data = item.get("metadata") if isinstance(item, dict) else None
            if not isinstance(data, dict):
                continue
            report = data.get("report") if isinstance(data.get("report"), dict) else None
            if report and isinstance(report.get("overall_score"), (int, float)):
                previous_score = float(report["overall_score"])
                break

        if previous_score is not None and isinstance(score, (int, float)):
            regression_count = 1 if score < previous_score else 0
            improved = score > previous_score

        if previous_score is None:
            reasoning = (
                f"Current monitoring baseline: SEO score {score}/100 across {resources_analyzed} resources. "
                "No previous workflow baseline was found yet, so regression comparison will start after another workflow run."
            )
            status = "baseline"
        elif regression_count:
            reasoning = f"Regression detected: SEO score moved from {previous_score} to {score}."
            status = "regression"
        elif improved:
            reasoning = f"Improvement detected: SEO score moved from {previous_score} to {score}."
            status = "improved"
        else:
            reasoning = f"No SEO score regression detected. Current score remains {score}/100."
            status = "stable"

        return AgentOutput(
            agent_name=self.name,
            reasoning=reasoning,
            result={
                "status": status,
                "current_audit": current,
                "current_score": score,
                "previous_score": previous_score,
                "regressions": regression_count,
                "findings_count": len(findings),
                "resources_analyzed": resources_analyzed,
                "next_check_recommendation": "Run monitoring again after the next approved fixes and sync.",
            },
            confidence=0.82 if previous_score is not None else 0.75,
            next_action=NextAction.COMPLETE,
        )
