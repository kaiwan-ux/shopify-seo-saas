"""Symmetric encryption for sensitive tokens at rest."""

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.config.settings import get_settings
from app.core.exceptions import IntegrationError


@lru_cache
def _get_fernet() -> Fernet:
    settings = get_settings()
    try:
        return Fernet(settings.token_encryption_key.encode())
    except Exception as exc:
        raise IntegrationError(
            "Invalid TOKEN_ENCRYPTION_KEY — must be a valid Fernet key",
            error_code="ENCRYPTION_CONFIG_ERROR",
            status_code=500,
        ) from exc


def encrypt_token(plain_text: str) -> str:
    """Encrypt a plaintext token for database storage."""
    return _get_fernet().encrypt(plain_text.encode()).decode()


def decrypt_token(cipher_text: str) -> str:
    """Decrypt a stored token."""
    try:
        return _get_fernet().decrypt(cipher_text.encode()).decode()
    except InvalidToken as exc:
        raise IntegrationError(
            "Failed to decrypt stored token — credentials may be corrupted",
            error_code="TOKEN_DECRYPT_ERROR",
            status_code=500,
        ) from exc
