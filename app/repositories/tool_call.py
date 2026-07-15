import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tool_call import ToolCall
from app.repositories.base import BaseRepository


class ToolCallRepository(BaseRepository[ToolCall]):
    model = ToolCall

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_log(
        self,
        tool_name: str,
        agent_name: str,
        status: str,
        store_id: uuid.UUID | None = None,
        arguments: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        duration_ms: int | None = None,
        attempt: int = 1,
        error_message: str | None = None,
        workflow_run_id: uuid.UUID | None = None,
        agent_run_id: uuid.UUID | None = None,
    ) -> ToolCall:
        log = ToolCall(
            tool_name=tool_name,
            agent_name=agent_name,
            status=status,
            store_id=store_id,
            arguments=arguments,
            result=result,
            duration_ms=duration_ms,
            attempt=attempt,
            error_message=error_message,
            workflow_run_id=workflow_run_id,
            agent_run_id=agent_run_id,
        )
        return await self.create(log)
