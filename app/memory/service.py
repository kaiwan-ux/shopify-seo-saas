"""Semantic memory service."""

import uuid
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory_entry import MemoryType
from app.rag.pipeline import RAGPipeline
from app.repositories.memory import MemoryRepository


class MemoryService:
    """Manages conversation, workflow, agent, and long-term memory."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = MemoryRepository(session)
        self.rag = RAGPipeline(session)

    async def store(
        self,
        key: str,
        content: str,
        memory_type: MemoryType,
        user_id: uuid.UUID | None = None,
        store_id: uuid.UUID | None = None,
        workflow_run_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> uuid.UUID:
        """Store memory in PostgreSQL and index in Qdrant."""
        qdrant_id: str | None = None
        try:
            qdrant_id = await self.rag.index_memory(
                key=key,
                content=content,
                memory_type=memory_type.value,
                metadata={
                    "user_id": str(user_id) if user_id else None,
                    "store_id": str(store_id) if store_id else None,
                    **(metadata or {}),
                },
            )
        except Exception as exc:
            logger.warning("Memory vector indexing skipped for key={}: {}", key, exc)

        entry = await self.repo.create(
            key=key,
            content=content,
            memory_type=memory_type.value,
            user_id=user_id,
            store_id=store_id,
            workflow_run_id=workflow_run_id,
            metadata_=metadata,
            qdrant_point_id=qdrant_id,
            collection_name=RAGPipeline.MEMORY_COLLECTION,
        )
        return entry.id

    async def retrieve(
        self,
        query: str,
        memory_type: MemoryType | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic memory retrieval via Qdrant."""
        return await self.rag.retrieve_memory(
            query,
            memory_type=memory_type.value if memory_type else None,
            top_k=top_k,
        )

    async def store_workflow_memory(
        self,
        workflow_id: uuid.UUID,
        store_id: uuid.UUID,
        state: dict[str, Any],
    ) -> None:
        """Persist workflow results as long-term memory."""
        audit = state.get("agent_outputs", {}).get("audit", {})
        summary = audit.get("result", {}).get("summary", "Workflow completed")

        await self.store(
            key=f"workflow:{workflow_id}",
            content=summary,
            memory_type=MemoryType.WORKFLOW,
            store_id=store_id,
            workflow_run_id=workflow_id,
            metadata={"status": state.get("status"), "task": state.get("task")},
        )

    async def get_by_user(
        self, user_id: uuid.UUID, memory_type: MemoryType | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        entries = await self.repo.list_by_user(user_id, memory_type, limit)
        return [
            {
                "id": str(e.id),
                "key": e.key,
                "content": e.content,
                "memory_type": e.memory_type,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ]
