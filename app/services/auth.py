import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.password import hash_password, verify_password
from app.config.settings import Settings, get_settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.models.user import User
from app.repositories.settings import SettingsRepository
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    """Authentication and token management service."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.user_repo = UserRepository(session)
        self.settings_repo = SettingsRepository(session)

    async def register(self, data: UserCreate) -> User:
        """Register a new user with default settings."""
        if await self.user_repo.email_exists(data.email):
            raise ConflictError("Email already registered", error_code="EMAIL_EXISTS")

        user = await self.user_repo.create_user(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        await self.settings_repo.create_default(user.id)
        return user

    async def login(self, data: UserLogin) -> tuple[User, TokenResponse]:
        """Authenticate user and return token pair."""
        user = await self.user_repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password", error_code="INVALID_CREDENTIALS")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated", error_code="ACCOUNT_INACTIVE")

        tokens = self._create_token_pair(user.id)
        return user, tokens

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Issue a new token pair from a valid refresh token."""
        payload = decode_token(refresh_token, expected_type="refresh", settings=self.settings)
        user_id = uuid.UUID(payload["sub"])

        user = await self.user_repo.get_active_by_id(user_id)
        if user is None:
            raise UnauthorizedError("User not found or inactive")

        return self._create_token_pair(user.id)

    def _create_token_pair(self, user_id: uuid.UUID) -> TokenResponse:
        access_token = create_access_token(user_id, self.settings)
        refresh_token = create_refresh_token(user_id, self.settings)
        expires_in = self.settings.jwt_access_token_expire_minutes * 60

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )
