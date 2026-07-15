import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_token
from app.config.settings import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user import UserRepository

security_scheme = HTTPBearer(auto_error=False)


async def get_settings_dep() -> Settings:
    return get_settings()


async def get_session(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AsyncSession:
    return session


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> User:
    """Resolve the authenticated user from a Bearer access token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Not authenticated", error_code="NOT_AUTHENTICATED")

    payload = decode_token(credentials.credentials, expected_type="access", settings=settings)
    user_id = uuid.UUID(payload["sub"])

    user_repo = UserRepository(session)
    user = await user_repo.get_active_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User not found or inactive")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise UnauthorizedError("Account is deactivated")
    return current_user


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_active_user)]
