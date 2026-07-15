import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import AppSettings
from app.repositories.base import BaseRepository


class SettingsRepository(BaseRepository[AppSettings]):
    """Repository for user application settings."""

    model = AppSettings

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> AppSettings | None:
        result = await self.session.execute(
            select(AppSettings).where(AppSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_default(self, user_id: uuid.UUID) -> AppSettings:
        settings = AppSettings(user_id=user_id, preferences={})
        return await self.create(settings)
