"""AI chat and workflow service."""

import uuid
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.shopify.services import ShopifyIntegrationService
from app.llm.factory import get_llm_provider
from app.memory.service import MemoryService
from app.models.memory_entry import MemoryType
from app.observability.telemetry import trace_operation
from app.rag.pipeline import RAGPipeline
from app.workflows.orchestrator import WorkflowOrchestrator


class AIService:
    """High-level AI service for chat and workflow management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.orchestrator = WorkflowOrchestrator(session)
        self.memory = MemoryService(session)
        self.rag = RAGPipeline(session)
        self.shopify = ShopifyIntegrationService(session)
        self.llm = get_llm_provider()

    async def chat(
        self,
        user_id: uuid.UUID,
        message: str,
        store_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Process a chat message — routes to workflow if SEO task detected."""
        async with trace_operation("ai.chat", {"user_id": str(user_id)}):
            rag_context = ""
            try:
                await self.rag.initialize()
                results = await self.rag.retrieve(message)
                rag_context = "\n".join(r["text"][:300] for r in results[:3])
            except Exception as exc:
                logger.warning("RAG retrieval in chat failed: {}", exc)

            await self.memory.store(
                key=f"chat:{user_id}",
                content=message,
                memory_type=MemoryType.CONVERSATION,
                user_id=user_id,
                store_id=store_id,
            )

            seo_keywords = {"seo", "audit", "optimize", "meta", "title", "description", "ranking", "search"}
            is_seo_task = any(kw in message.lower() for kw in seo_keywords)

            if is_seo_task and store_id:
                result = await self.orchestrator.start_workflow(
                    user_id=user_id,
                    store_id=store_id,
                    task=message,
                )
                return {
                    "type": "workflow",
                    "message": "SEO workflow started",
                    "workflow": result,
                }

            response = await self.llm.invoke_prompt(
                system=(
                    "You are an AI assistant for a Shopify SEO SaaS platform. "
                    "Help users with SEO questions. Be concise and actionable."
                    + (f"\n\nRelevant knowledge:\n{rag_context}" if rag_context else "")
                ),
                user=message,
            )

            return {
                "type": "chat",
                "message": response.content,
                "tokens_used": response.tokens_used,
                "latency_ms": response.latency_ms,
            }

    async def start_workflow(
        self, user_id: uuid.UUID, store_id: uuid.UUID, task: str
    ) -> dict[str, Any]:
        async with trace_operation("ai.workflow.start"):
            return await self.orchestrator.start_workflow(user_id, store_id, task)

    async def get_workflow(self, workflow_id: uuid.UUID) -> dict[str, Any] | None:
        return await self.orchestrator.get_workflow(workflow_id)

    async def run_agent(
        self, agent_name: str, user_id: uuid.UUID, store_id: uuid.UUID, task: str
    ) -> dict[str, Any]:
        async with trace_operation("ai.agent.run", {"agent": agent_name}):
            return await self.orchestrator.run_single_agent(
                agent_name, user_id, store_id, task
            )
