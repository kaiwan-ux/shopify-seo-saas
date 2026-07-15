"""Prompt management with versioning and templates."""

import json
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt_version import PromptVersion
from app.repositories.prompt_version import PromptVersionRepository

PROMPTS_DIR = Path(__file__).parent / "templates"


class PromptTemplate(BaseModel):
    """In-memory prompt template."""

    name: str
    agent_name: str
    system_prompt: str
    developer_prompt: str | None = None
    tool_instructions: str | None = None
    output_schema: dict[str, Any] | None = None
    variables: list[str] = Field(default_factory=list)
    version: int = 1


class PromptManager:
    """Loads, versions, and renders agent prompts."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session
        self._cache: dict[str, PromptTemplate] = {}
        self._repo = PromptVersionRepository(session) if session else None

    def load_from_file(self, filename: str) -> PromptTemplate:
        """Load a prompt template from the templates directory."""
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        template = PromptTemplate(**data)
        self._cache[template.name] = template
        return template

    def load_all_templates(self) -> dict[str, PromptTemplate]:
        """Load all JSON templates from the templates directory."""
        if not PROMPTS_DIR.exists():
            PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
            return {}

        for path in PROMPTS_DIR.glob("*.json"):
            try:
                self.load_from_file(path.name)
            except Exception as exc:
                logger.warning("Failed to load prompt template {}: {}", path.name, exc)

        return dict(self._cache)

    def get(self, name: str) -> PromptTemplate:
        """Get a prompt template by name (loads from file if not cached)."""
        if name not in self._cache:
            self.load_from_file(f"{name}.json")
        return self._cache[name]

    def render(self, name: str, variables: dict[str, Any]) -> tuple[str, str | None]:
        """Render system and developer prompts with variable substitution."""
        template = self.get(name)
        system = template.system_prompt.format(**variables)
        developer = (
            template.developer_prompt.format(**variables) if template.developer_prompt else None
        )
        return system, developer

    async def sync_to_database(self) -> int:
        """Persist file-based templates to the database."""
        if self._repo is None:
            raise RuntimeError("Database session required for sync_to_database")

        templates = self.load_all_templates()
        count = 0
        for template in templates.values():
            await self._repo.upsert(template)
            count += 1
        return count

    async def get_active_from_db(self, agent_name: str) -> PromptTemplate | None:
        """Get the active prompt version from the database."""
        if self._repo is None:
            return None
        record = await self._repo.get_active_by_agent(agent_name)
        if record is None:
            return None
        return PromptTemplate(
            name=record.name,
            agent_name=record.agent_name,
            system_prompt=record.system_prompt,
            developer_prompt=record.developer_prompt,
            tool_instructions=record.tool_instructions,
            output_schema=record.output_schema,
            variables=record.variables or [],
            version=record.version,
        )
