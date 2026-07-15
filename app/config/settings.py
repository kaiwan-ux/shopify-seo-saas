from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Shopify SEO SaaS", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = Field(default=False, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Database
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_user: str = Field(default="seo_user", alias="POSTGRES_USER")
    postgres_password: str = Field(default="", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="seo_db", alias="POSTGRES_DB")
    database_url: PostgresDsn | str = Field(
        default="postgresql+asyncpg://seo_user:password@localhost:5432/seo_db",
        alias="DATABASE_URL",
    )

    # Security
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:3000"], alias="CORS_ORIGINS"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=False, alias="LOG_JSON")

    # Application URL (used for OAuth callbacks and webhooks)
    app_url: str = Field(default="http://localhost:8000", alias="APP_URL")

    # Token encryption — generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    token_encryption_key: str = Field(..., alias="TOKEN_ENCRYPTION_KEY")

    # Shopify Partner App
    shopify_api_key: str = Field(..., alias="SHOPIFY_API_KEY")
    shopify_api_secret: str = Field(..., alias="SHOPIFY_API_SECRET")
    shopify_scopes: str = Field(
        default="read_products,write_products,read_content,write_content,read_online_store_pages,read_redirects,write_redirects,read_inventory",
        alias="SHOPIFY_SCOPES",
    )
    shopify_api_version: str = Field(default="2025-01", alias="SHOPIFY_API_VERSION")
    shopify_oauth_state_expire_minutes: int = Field(default=10, alias="SHOPIFY_OAUTH_STATE_EXPIRE_MINUTES")

    # MCP
    mcp_server_url: str | None = Field(default=None, alias="MCP_SERVER_URL")
    mcp_server_command: str | None = Field(default=None, alias="MCP_SERVER_COMMAND")
    mcp_bearer_token: str | None = Field(default=None, alias="MCP_BEARER_TOKEN")
    mcp_transport: str = Field(default="streamable-http", alias="MCP_TRANSPORT")
    mcp_request_timeout_seconds: int = Field(default=60, alias="MCP_REQUEST_TIMEOUT_SECONDS")
    mcp_max_retries: int = Field(default=3, alias="MCP_MAX_RETRIES")

    # Sync scheduler
    sync_enabled: bool = Field(default=True, alias="SYNC_ENABLED")
    sync_interval_hours: int = Field(default=6, alias="SYNC_INTERVAL_HOURS")
    sync_batch_size: int = Field(default=50, alias="SYNC_BATCH_SIZE")

    # --- Phase 3: AI Infrastructure ---

    # LLM Provider
    llm_provider: Literal["openai", "anthropic", "gemini", "ollama", "groq"] = Field(
        default="openai", alias="LLM_PROVIDER"
    )
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=4096, alias="LLM_MAX_TOKENS")
    llm_timeout_seconds: int = Field(default=120, alias="LLM_TIMEOUT_SECONDS")

    # LLM API Keys (provider-specific)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_api_key_fallback: str | None = Field(default=None, alias="GROQ_API_KEY_FALLBACK")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    # Embeddings
    embedding_provider: Literal["openai", "nomic", "bge", "none"] = Field(
        default="openai", alias="EMBEDDING_PROVIDER"
    )
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")

    # Qdrant Vector Database
    qdrant_host: str = Field(default="qdrant", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection_prefix: str = Field(default="seo", alias="QDRANT_COLLECTION_PREFIX")

    # RAG
    rag_chunk_size: int = Field(default=512, alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=64, alias="RAG_CHUNK_OVERLAP")
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")

    # AI Workflow
    ai_max_retries: int = Field(default=3, alias="AI_MAX_RETRIES")
    ai_tool_timeout_seconds: int = Field(default=60, alias="AI_TOOL_TIMEOUT_SECONDS")
    ai_require_approval_for_writes: bool = Field(default=True, alias="AI_REQUIRE_APPROVAL_FOR_WRITES")

    # LangSmith (optional)
    langsmith_enabled: bool = Field(default=False, alias="LANGSMITH_ENABLED")
    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="shopify-seo-saas", alias="LANGSMITH_PROJECT")

    # OpenTelemetry
    otel_enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    otel_service_name: str = Field(default="shopify-seo-saas", alias="OTEL_SERVICE_NAME")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator(
        "mcp_server_url",
        "mcp_server_command",
        "mcp_bearer_token",
        "openai_api_key",
        "anthropic_api_key",
        "google_api_key",
        "groq_api_key",
        "groq_api_key_fallback",
        "qdrant_api_key",
        "langsmith_api_key",
        mode="before",
    )
    @classmethod
    def empty_str_to_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def openapi_url(self) -> str | None:
        return None if self.is_production else f"{self.api_v1_prefix}/openapi.json"

    @property
    def docs_url(self) -> str | None:
        return None if self.is_production else f"{self.api_v1_prefix}/docs"

    @property
    def redoc_url(self) -> str | None:
        return None if self.is_production else f"{self.api_v1_prefix}/redoc"

    @property
    def shopify_redirect_uri(self) -> str:
        return f"{self.app_url.rstrip('/')}{self.api_v1_prefix}/shopify/callback"

    @property
    def shopify_webhook_base_url(self) -> str:
        return f"{self.app_url.rstrip('/')}{self.api_v1_prefix}/shopify/webhooks"

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
