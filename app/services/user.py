import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    """User profile management service."""

    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)
        return user
