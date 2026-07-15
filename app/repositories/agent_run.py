import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.shared.models import AgentOutput
from app.models.agent_run import AgentRun, AgentRunStatus
from app.repositories.base import BaseRepository


class AgentRunRepository(BaseRepository[AgentRun]):
    model = AgentRun

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_run(
        self,
        workflow_run_id: uuid.UUID,
        agent_name: str,
        output: AgentOutput,
    ) -> AgentRun:
        run = AgentRun(
            workflow_run_id=workflow_run_id,
            agent_name=agent_name,
            status=AgentRunStatus.COMPLETED if output.confidence > 0 else AgentRunStatus.FAILED,
            reasoning=output.reasoning,
            result=output.result,
            confidence=output.confidence,
            next_action=output.next_action.value,
            required_tools=output.required_tools,
            completed_at=datetime.now(UTC),
        )
        return await self.create(run)

    async def list_by_workflow(self, workflow_run_id: uuid.UUID) -> list[AgentRun]:
        result = await self.session.execute(
            select(AgentRun)
            .where(AgentRun.workflow_run_id == workflow_run_id)
            .order_by(AgentRun.created_at)
        )
        return list(result.scalars().all())
