import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mcp_tool_log import MCPToolLog
from app.repositories.base import BaseRepository


class MCPToolLogRepository(BaseRepository[MCPToolLog]):
    model = MCPToolLog

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_log(
        self,
        tool_name: str,
        status: str,
        store_id: uuid.UUID | None = None,
        arguments: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        duration_ms: int | None = None,
        attempt: int = 1,
        error_message: str | None = None,
        executed_by: str | None = None,
    ) -> MCPToolLog:
        log = MCPToolLog(
            store_id=store_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            status=status,
            duration_ms=duration_ms,
            attempt=attempt,
            error_message=error_message,
            executed_by=executed_by,
        )
        return await self.create(log)
