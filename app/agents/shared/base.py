"""Base agent class for all SEO agents."""

import json
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction
from app.llm.factory import get_llm_provider
from app.llm.provider import BaseLLMProvider
from app.prompts.manager import PromptManager
from app.rag.pipeline import RAGPipeline
from app.tools.executor import AgentToolExecutor


class BaseAgent(ABC):
    """Abstract base for all SEO agents."""

    name: AgentName

    def __init__(
        self,
        session: AsyncSession,
        llm: BaseLLMProvider | None = None,
        tool_executor: AgentToolExecutor | None = None,
        prompt_manager: PromptManager | None = None,
        rag: RAGPipeline | None = None,
    ) -> None:
        self.session = session
        self.llm = llm or get_llm_provider()
        self.tools = tool_executor or AgentToolExecutor(session)
        self.prompts = prompt_manager or PromptManager(session)
        self.rag = rag or RAGPipeline(session)

    async def run(self, context: AgentContext) -> AgentOutput:
        """Execute the agent and return structured output."""
        start = time.perf_counter()
        logger.info("Agent {} starting for workflow={}", self.name, context.workflow_id)

        try:
            output = await self._execute(context)
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "Agent {} completed in {}ms confidence={:.2f} next={}",
                self.name,
                duration_ms,
                output.confidence,
                output.next_action,
            )
            return output
        except Exception as exc:
            logger.exception("Agent {} failed: {}", self.name, exc)
            return AgentOutput(
                agent_name=self.name,
                reasoning=f"Agent failed: {exc}",
                result={"error": str(exc)},
                confidence=0.0,
                next_action=NextAction.RETRY,
            )

    @abstractmethod
    async def _execute(self, context: AgentContext) -> AgentOutput:
        """Agent-specific execution logic."""

    async def _invoke_llm(
        self,
        prompt_name: str,
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Render prompt and invoke LLM, parsing JSON response."""
        system, developer = self.prompts.render(prompt_name, variables)
        user_msg = developer or "Execute your task and return valid JSON."

        response = await self.llm.invoke_prompt(system=system, user=user_msg)

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_response": response.content, "parse_error": True}

    async def _get_rag_context(self, query: str) -> str:
        """Retrieve relevant knowledge for the agent."""
        try:
            results = await self.rag.retrieve(query)
            if not results:
                return ""
            return "\n\n".join(
                f"[{r['source']}] {r['title']}: {r['text'][:500]}" for r in results
            )
        except Exception as exc:
            logger.warning("RAG retrieval failed for agent {}: {}", self.name, exc)
            return ""

    async def _fetch_store_data(self, store_id: str) -> dict[str, Any]:
        """Fetch basic store data via tool executor."""
        sid = uuid.UUID(store_id)
        products = await self.tools.execute(
            "get_products", {"store_id": store_id, "limit": 200},
            store_id=sid, agent_name=self.name,
        )
        collections = await self.tools.execute(
            "get_collections", {"store_id": store_id, "limit": 200},
            store_id=sid, agent_name=self.name,
        )
        pages = await self.tools.execute(
            "get_pages", {"store_id": store_id, "limit": 100},
            store_id=sid, agent_name=self.name,
        )
        return {
            "products": products.get("products", []),
            "collections": collections.get("collections", []),
            "pages": pages.get("pages", []),
        }
