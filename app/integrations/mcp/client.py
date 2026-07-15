"""Async MCP client for connecting to the Shopify MCP Server."""

from contextlib import asynccontextmanager
from typing import Any

import httpx
from loguru import logger

from app.core.exceptions import IntegrationError
from app.integrations.mcp.config import MCPConfig
from app.utils.retry import with_retry


class MCPClient:
    """Connects to a Shopify MCP Server and exposes tool discovery/execution."""

    def __init__(self, config: MCPConfig | None = None) -> None:
        self.config = config or MCPConfig.from_settings()
        self._discovered_tools: list[dict[str, Any]] = []

    @property
    def is_available(self) -> bool:
        return self.config.is_configured

    async def discover_tools(self) -> list[dict[str, Any]]:
        """Discover available tools from the MCP server."""
        if not self.config.is_configured:
            logger.warning("MCP server not configured — returning empty tool list")
            return []

        if self.config.server_url:
            tools = await self._discover_via_http()
        else:
            tools = await self._discover_via_stdio()

        self._discovered_tools = tools
        logger.info("Discovered {} MCP tools", len(tools))
        return tools

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool on the MCP server."""
        if not self.config.is_configured:
            raise IntegrationError(
                "MCP server is not configured",
                error_code="MCP_NOT_CONFIGURED",
            )

        return await with_retry(
            lambda: self._call_tool_once(tool_name, arguments),
            max_attempts=self.config.max_retries,
            operation_name=f"mcp_tool:{tool_name}",
            retry_on=(httpx.TransportError, httpx.TimeoutException, IntegrationError),
        )

    async def _discover_via_http(self) -> list[dict[str, Any]]:
        """Discover tools via Streamable HTTP transport."""
        url = f"{self.config.server_url.rstrip('/')}/tools/list"
        headers = self._auth_headers()

        async with httpx.AsyncClient(timeout=self.config.request_timeout_seconds) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise IntegrationError(
                f"MCP tool discovery failed (HTTP {response.status_code})",
                error_code="MCP_DISCOVERY_ERROR",
            )

        data = response.json()
        return data.get("tools", [])

    async def _discover_via_stdio(self) -> list[dict[str, Any]]:
        """Discover tools via stdio MCP transport using the Python MCP SDK."""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as exc:
            raise IntegrationError(
                "MCP Python SDK not installed",
                error_code="MCP_SDK_MISSING",
            ) from exc

        command_parts = (self.config.server_command or "").split()
        if not command_parts:
            raise IntegrationError("MCP_SERVER_COMMAND is not set", error_code="MCP_NOT_CONFIGURED")

        server_params = StdioServerParameters(
            command=command_parts[0],
            args=command_parts[1:],
        )

        tools: list[dict[str, Any]] = []
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                tools = [
                    {
                        "name": t.name,
                        "description": t.description or "",
                        "inputSchema": t.inputSchema if hasattr(t, "inputSchema") else {},
                    }
                    for t in result.tools
                ]

        return tools

    async def _call_tool_once(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.config.server_url:
            return await self._call_tool_via_http(tool_name, arguments)
        return await self._call_tool_via_stdio(tool_name, arguments)

    async def _call_tool_via_http(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        url = f"{self.config.server_url.rstrip('/')}/tools/call"
        headers = self._auth_headers()
        payload = {"name": tool_name, "arguments": arguments}

        async with httpx.AsyncClient(timeout=self.config.request_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise IntegrationError(
                f"MCP tool call failed (HTTP {response.status_code}): {response.text[:300]}",
                error_code="MCP_TOOL_ERROR",
            )

        return response.json()

    async def _call_tool_via_stdio(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        command_parts = (self.config.server_command or "").split()
        server_params = StdioServerParameters(
            command=command_parts[0],
            args=command_parts[1:],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                content = [
                    {"type": c.type, "text": c.text if hasattr(c, "text") else str(c)}
                    for c in result.content
                ]
                return {"content": content, "isError": result.isError}

    def _auth_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.bearer_token:
            headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        return headers

    @asynccontextmanager
    async def session(self):
        """Context manager ensuring MCP client is ready."""
        if not self._discovered_tools and self.is_available:
            await self.discover_tools()
        yield self
