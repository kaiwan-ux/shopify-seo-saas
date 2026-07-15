"""Encrypted Shopify access token lifecycle management."""

import uuid
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import IntegrationError, NotFoundError, ShopifyAuthError
from app.models.store import Store
from app.repositories.store import StoreRepository
from app.utils.encryption import decrypt_token, encrypt_token


class ShopifyTokenManager:
    """Manages encrypted Shopify access tokens for connected stores."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.store_repo = StoreRepository(session)

    async def store_token(
        self,
        store: Store,
        access_token: str,
        scopes: str,
    ) -> Store:
        """Encrypt and persist an access token on a store record."""
        store.encrypted_access_token = encrypt_token(access_token)
        store.scopes = scopes
        store.is_connected = True
        store.installed_at = datetime.now(UTC)
        store.uninstalled_at = None
        store.last_sync_error = None
        await self.session.flush()
        await self.session.refresh(store)
        logger.info("Stored encrypted token for store={}", store.shop_domain)
        return store

    async def get_access_token(self, store: Store) -> str:
        """Decrypt and return the access token for API calls."""
        if not store.is_connected or not store.encrypted_access_token:
            raise ShopifyAuthError(
                "Store is not connected or token is missing",
                error_code="STORE_NOT_CONNECTED",
            )

        try:
            return decrypt_token(store.encrypted_access_token)
        except IntegrationError:
            store.is_connected = False
            store.last_sync_error = "Token decryption failed — reconnection required"
            await self.session.flush()
            raise

    async def get_access_token_by_store_id(self, store_id: uuid.UUID) -> tuple[Store, str]:
        """Load store and return decrypted access token."""
        store = await self.store_repo.get_by_id(store_id)
        if store is None:
            raise NotFoundError("Store not found")
        token = await self.get_access_token(store)
        return store, token

    async def revoke_token(self, store: Store) -> Store:
        """Clear stored credentials on disconnect or uninstall."""
        store.encrypted_access_token = None
        store.scopes = None
        store.is_connected = False
        store.uninstalled_at = datetime.now(UTC)
        store.sync_status = "idle"
        await self.session.flush()
        await self.session.refresh(store)
        logger.info("Revoked token for store={}", store.shop_domain)
        return store

    async def mark_token_expired(self, store: Store, error: str) -> None:
        """Mark store credentials as invalid after an auth failure."""
        store.is_connected = False
        store.last_sync_error = error
        await self.session.flush()
        logger.warning("Marked store={} token as expired: {}", store.shop_domain, error)
