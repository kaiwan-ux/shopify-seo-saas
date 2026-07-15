"""Versioned prompt templates for AI agents."""

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PromptVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Versioned prompt template with system, developer, and tool instructions."""

    __tablename__ = "prompt_versions"
    __table_args__ = (UniqueConstraint("name", "version", name="uq_prompt_name_version"),)

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    developer_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    tool_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    variables: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<PromptVersion name={self.name} v={self.version}>"
