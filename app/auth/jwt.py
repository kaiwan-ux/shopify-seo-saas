from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.config.settings import Settings, get_settings
from app.core.exceptions import UnauthorizedError


def _create_token(
    subject: UUID | str,
    token_type: str,
    expires_delta: timedelta,
    settings: Settings | None = None,
) -> str:
    """Create a signed JWT token."""
    settings = settings or get_settings()
    now = datetime.now(UTC)
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: UUID | str,
    settings: Settings | None = None,
) -> str:
    """Create a short-lived access token."""
    settings = settings or get_settings()
    expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return _create_token(subject, "access", expires, settings)


def create_refresh_token(
    subject: UUID | str,
    settings: Settings | None = None,
) -> str:
    """Create a long-lived refresh token."""
    settings = settings or get_settings()
    expires = timedelta(days=settings.jwt_refresh_token_expire_days)
    return _create_token(subject, "refresh", expires, settings)


def decode_token(token: str, expected_type: str, settings: Settings | None = None) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise UnauthorizedError(f"Invalid token type: expected {expected_type}")

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("Token missing subject")

    return payload
