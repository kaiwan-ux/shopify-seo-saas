"""Performance Agent — Core Web Vitals analysis."""

import json

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction


class PerformanceAgent(BaseAgent):
    name = AgentName.PERFORMANCE

    async def _execute(self, context: AgentContext) -> AgentOutput:
        store_data = await self._fetch_store_data(context.store_id)

        result = await self._invoke_llm("performance", {
            "store_id": context.store_id,
            "store_data": json.dumps(store_data, default=str)[:3000],
        })

        return AgentOutput(
            agent_name=self.name,
            reasoning=f"Performance score: {result.get('score', 'N/A')}",
            result=result,
            confidence=0.7,
            next_action=NextAction.CONTINUE,
        )
