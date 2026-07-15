"""Central registry for MCP tools — used by AI agents in Phase 3."""

from typing import Any

from loguru import logger

from app.integrations.mcp.client import MCPClient
from app.integrations.mcp.config import MCPConfig
from app.integrations.mcp.tools import MCPToolDefinition, SHOPIFY_MCP_TOOLS


class MCPToolRegistry:
    """Discovers, caches, and exposes available MCP tools."""

    def __init__(self, config: MCPConfig | None = None) -> None:
        self.config = config or MCPConfig.from_settings()
        self.client = MCPClient(self.config)
        self._local_tools: dict[str, MCPToolDefinition] = {
            t.name: t for t in SHOPIFY_MCP_TOOLS
        }
        self._remote_tools: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Discover remote tools and merge with local definitions."""
        if self._initialized:
            return

        if self.client.is_available:
            try:
                remote = await self.client.discover_tools()
                self._remote_tools = {t["name"]: t for t in remote}
                logger.info(
                    "MCP registry initialized: {} remote, {} local tools",
                    len(self._remote_tools),
                    len(self._local_tools),
                )
            except Exception as exc:
                logger.warning("MCP remote discovery failed, using local tools only: {}", exc)
        else:
            logger.info("MCP server not configured — registry using {} local tools", len(self._local_tools))

        self._initialized = True

    def list_tools(self) -> list[dict[str, Any]]:
        """Return all registered tools (remote preferred over local)."""
        tools: list[dict[str, Any]] = []

        seen: set[str] = set()
        for name, remote in self._remote_tools.items():
            tools.append({
                "name": name,
                "description": remote.get("description", ""),
                "input_schema": remote.get("inputSchema", {}),
                "source": "remote",
            })
            seen.add(name)

        for name, local in self._local_tools.items():
            if name not in seen:
                tools.append({
                    "name": name,
                    "description": local.description,
                    "input_schema": local.input_schema,
                    "source": "local",
                    "category": local.category,
                })

        return tools

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """Look up a tool by name."""
        if name in self._remote_tools:
            remote = self._remote_tools[name]
            return {
                "name": name,
                "description": remote.get("description", ""),
                "input_schema": remote.get("inputSchema", {}),
                "source": "remote",
            }
        if name in self._local_tools:
            local = self._local_tools[name]
            return {
                "name": name,
                "description": local.description,
                "input_schema": local.input_schema,
                "source": "local",
                "category": local.category,
            }
        return None

    def has_tool(self, name: str) -> bool:
        return name in self._remote_tools or name in self._local_tools
