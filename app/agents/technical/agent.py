"""Technical SEO Agent — consumes the reusable Phase 4 technical engine."""

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction
from app.intelligence.adapters import resources_from_store_data
from app.intelligence.technical import TechnicalSEOEngine
from app.schemas.seo import CrawlURL, TechnicalAuditRequest


class TechnicalAgent(BaseAgent):
    name = AgentName.TECHNICAL

    async def _execute(self, context: AgentContext) -> AgentOutput:
        store_data = context.store_data or await self._fetch_store_data(context.store_id)
        resources = resources_from_store_data(store_data)
        urls = [
            CrawlURL(
                url=item.url,
                status_code=int(item.metadata.get("status_code", 200)),
                canonical_url=item.canonical_url,
                robots_index=item.indexable,
                in_sitemap=bool(item.metadata.get("in_sitemap", True)),
            )
            for item in resources
        ]
        base_url = str(
            store_data.get("shop_domain") or store_data.get("base_url") or "https://store.invalid"
        )
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
        result = await TechnicalSEOEngine().analyze(
            TechnicalAuditRequest(
                store_id=context.store_id,
                base_url=base_url,
                robots_txt=store_data.get("robots_txt"),
                sitemap_urls=list(store_data.get("sitemap_urls") or []),
                urls=urls,
            )
        )
        return AgentOutput(
            agent_name=self.name,
            reasoning=result.summary,
            result=result.model_dump(mode="json"),
            confidence=result.confidence,
            next_action=NextAction.CONTINUE,
            required_tools=["get_products", "get_collections", "get_pages"],
        )
