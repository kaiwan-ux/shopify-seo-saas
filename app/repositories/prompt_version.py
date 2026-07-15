from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt_version import PromptVersion
if TYPE_CHECKING:
    from app.prompts.manager import PromptTemplate
from app.repositories.base import BaseRepository


class PromptVersionRepository(BaseRepository[PromptVersion]):
    model = PromptVersion

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def upsert(self, template: PromptTemplate) -> PromptVersion:
        result = await self.session.execute(
            select(PromptVersion).where(
                PromptVersion.name == template.name,
                PromptVersion.version == template.version,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.system_prompt = template.system_prompt
            existing.developer_prompt = template.developer_prompt
            existing.tool_instructions = template.tool_instructions
            existing.output_schema = template.output_schema
            existing.variables = template.variables
            await self.session.flush()
            return existing

        record = PromptVersion(
            name=template.name,
            version=template.version,
            agent_name=template.agent_name,
            system_prompt=template.system_prompt,
            developer_prompt=template.developer_prompt,
            tool_instructions=template.tool_instructions,
            output_schema=template.output_schema,
            variables=template.variables,
        )
        return await self.create(record)

    async def get_active_by_agent(self, agent_name: str) -> PromptVersion | None:
        result = await self.session.execute(
            select(PromptVersion)
            .where(PromptVersion.agent_name == agent_name, PromptVersion.is_active.is_(True))
            .order_by(PromptVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[PromptVersion]:
        result = await self.session.execute(
            select(PromptVersion).where(PromptVersion.is_active.is_(True)).order_by(PromptVersion.name)
        )
        return list(result.scalars().all())
