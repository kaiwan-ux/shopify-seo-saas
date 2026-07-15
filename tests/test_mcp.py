"""Tests for MCP tool registry and executor."""

import uuid

import pytest

from app.integrations.mcp.registry import MCPToolRegistry
from app.integrations.mcp.tools import SHOPIFY_MCP_TOOLS


@pytest.mark.asyncio
async def test_tool_registry_local_tools(test_settings):
    from app.integrations.mcp.config import MCPConfig

    config = MCPConfig.from_settings(test_settings)
    registry = MCPToolRegistry(config)
    await registry.initialize()

    tools = registry.list_tools()
    assert len(tools) >= len(SHOPIFY_MCP_TOOLS)

    assert registry.has_tool("get_products")
    assert registry.has_tool("sync_store")
    assert registry.get_tool("get_products") is not None


@pytest.mark.asyncio
async def test_mcp_executor_unknown_tool(db_session, test_settings):
    from app.integrations.mcp.executor import MCPToolExecutor

    executor = MCPToolExecutor(db_session)
    with pytest.raises(Exception):
        await executor.execute("nonexistent_tool", {}, executed_by="test")
