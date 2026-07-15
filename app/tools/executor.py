"""Centralized tool executor for AI agents — wraps MCP executor."""

import asyncio
import time
import uuid
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.integrations.mcp.executor import MCPToolExecutor
from app.models.tool_call import ToolCallStatus
from app.repositories.tool_call import ToolCallRepository


class AgentToolExecutor:
    """AI agent tool layer — all Shopify access goes through here.

    Architecture:
        Agent → AgentToolExecutor → MCPToolExecutor → Shopify MCP → Shopify
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()
        self.mcp = MCPToolExecutor(session)
        self.log_repo = ToolCallRepository(session)

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        store_id: uuid.UUID | None = None,
        agent_name: str = "unknown",
        workflow_run_id: uuid.UUID | None = None,
        agent_run_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Execute a tool with timeout, logging, and validation."""
        start = time.perf_counter()
        attempt = 1
        max_attempts = self.settings.ai_max_retries
        last_error: str | None = None

        while attempt <= max_attempts:
            try:
                result = await asyncio.wait_for(
                    self.mcp.execute(
                        tool_name,
                        arguments,
                        store_id=store_id,
                        executed_by=f"agent:{agent_name}",
                    ),
                    timeout=self.settings.ai_tool_timeout_seconds,
                )

                duration_ms = int((time.perf_counter() - start) * 1000)
                await self.log_repo.create_log(
                    tool_name=tool_name,
                    agent_name=agent_name,
                    arguments=arguments,
                    result=result,
                    status=ToolCallStatus.SUCCESS,
                    duration_ms=duration_ms,
                    attempt=attempt,
                    store_id=store_id,
                    workflow_run_id=workflow_run_id,
                    agent_run_id=agent_run_id,
                )

                logger.info(
                    "Tool {} executed by {} in {}ms (attempt {})",
                    tool_name, agent_name, duration_ms, attempt,
                )
                return result

            except TimeoutError:
                last_error = f"Tool {tool_name} timed out after {self.settings.ai_tool_timeout_seconds}s"
            except Exception as exc:
                last_error = str(exc)

            duration_ms = int((time.perf_counter() - start) * 1000)
            await self.log_repo.create_log(
                tool_name=tool_name,
                agent_name=agent_name,
                arguments=arguments,
                status=ToolCallStatus.FAILED if attempt >= max_attempts else ToolCallStatus.TIMEOUT,
                duration_ms=duration_ms,
                attempt=attempt,
                error_message=last_error,
                store_id=store_id,
                workflow_run_id=workflow_run_id,
                agent_run_id=agent_run_id,
            )

            if attempt >= max_attempts:
                raise RuntimeError(f"Tool {tool_name} failed after {max_attempts} attempts: {last_error}")

            attempt += 1
            logger.warning("Tool {} attempt {} failed, retrying: {}", tool_name, attempt - 1, last_error)

        raise RuntimeError(f"Tool {tool_name} exhausted retries")

    async def list_available_tools(self) -> list[dict[str, Any]]:
        """List tools available to agents."""
        await self.mcp.registry.initialize()
        return self.mcp.registry.list_tools()
