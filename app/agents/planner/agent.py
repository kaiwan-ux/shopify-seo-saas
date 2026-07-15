"""Planner Agent — orchestration only, never performs SEO work."""

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction


class PlannerAgent(BaseAgent):
    name = AgentName.PLANNER

    async def _execute(self, context: AgentContext) -> AgentOutput:
        store_data = await self._fetch_store_data(context.store_id)

        result = await self._invoke_llm("planner", {
            "store_id": context.store_id,
            "task": context.task,
        })

        execution_order = result.get(
            "execution_order",
            ["audit", "technical", "performance", "content", "reporting", "monitoring"],
        )

        return AgentOutput(
            agent_name=self.name,
            reasoning=result.get("merge_strategy", "Standard SEO workflow planned"),
            result={
                "plan": result,
                "execution_order": execution_order,
                "store_summary": {
                    "products": len(store_data.get("products", [])),
                    "collections": len(store_data.get("collections", [])),
                    "pages": len(store_data.get("pages", [])),
                },
            },
            confidence=0.9 if "execution_order" in result else 0.5,
            next_action=NextAction.CONTINUE,
            required_tools=["get_products", "get_collections", "get_pages"],
        )
