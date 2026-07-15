"""MCP client configuration."""

from dataclasses import dataclass

from app.config.settings import Settings, get_settings


@dataclass(frozen=True)
class MCPConfig:
    """Configuration for connecting to the Shopify MCP Server."""

    server_url: str | None
    server_command: str | None
    bearer_token: str | None
    transport: str
    request_timeout_seconds: int
    max_retries: int

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "MCPConfig":
        settings = settings or get_settings()
        return cls(
            server_url=settings.mcp_server_url,
            server_command=settings.mcp_server_command,
            bearer_token=settings.mcp_bearer_token,
            transport=settings.mcp_transport,
            request_timeout_seconds=settings.mcp_request_timeout_seconds,
            max_retries=settings.mcp_max_retries,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.server_url or self.server_command)
