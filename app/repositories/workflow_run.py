import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_run import WorkflowRun, WorkflowStatus
from app.repositories.base import BaseRepository


class WorkflowRunRepository(BaseRepository[WorkflowRun]):
    model = WorkflowRun

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_run(
        self,
        user_id: uuid.UUID,
        store_id: uuid.UUID,
        task: str,
    ) -> WorkflowRun:
        run = WorkflowRun(
            user_id=user_id,
            store_id=store_id,
            task=task,
            status=WorkflowStatus.PENDING,
        )
        return await self.create(run)

    async def complete(
        self,
        run: WorkflowRun,
        status: str,
        graph_state: dict[str, Any],
        duration_ms: int,
    ) -> WorkflowRun:
        run.status = status
        run.graph_state = graph_state
        run.completed_at = datetime.now(UTC)
        run.duration_ms = duration_ms
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def fail(self, run: WorkflowRun, error: str) -> WorkflowRun:
        run.status = WorkflowStatus.FAILED
        run.error_message = error
        run.completed_at = datetime.now(UTC)
        await self.session.flush()
        return run
