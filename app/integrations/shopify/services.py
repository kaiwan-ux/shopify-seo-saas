"""High-level Shopify integration service orchestrating OAuth, sync, and webhooks."""

import uuid
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ShopifyAuthError
from app.integrations.shopify.graphql import ShopifyGraphQLClient
from app.integrations.shopify.oauth import ShopifyOAuthService, normalize_shop_domain
from app.integrations.shopify.sync import ShopifySyncEngine
from app.integrations.shopify.token_manager import ShopifyTokenManager
from app.integrations.shopify.webhooks import ShopifyWebhookHandler
from app.models.store import Store
from app.models.sync_log import SyncType
from app.models.user import User
from app.repositories.store import StoreRepository


class ShopifyIntegrationService:
    """Orchestrates Shopify app installation, sync, and disconnection."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.store_repo = StoreRepository(session)
        self.oauth = ShopifyOAuthService(self.settings)
        self.token_manager = ShopifyTokenManager(session)
        self.sync_engine = ShopifySyncEngine(session, self.settings)
        self.webhook_handler = ShopifyWebhookHandler(session, self.settings)

    async def initiate_connection(self, user: User, shop_domain: str) -> dict[str, str]:
        """Start OAuth flow — returns authorization URL for the merchant."""
        shop = normalize_shop_domain(shop_domain)

        existing = await self.store_repo.get_by_shop_domain(shop)
        if existing and existing.is_connected and existing.owner_id != user.id:
            raise ConflictError(
                "This shop is already connected to another account",
                error_code="SHOP_ALREADY_CONNECTED",
            )

        auth_url, state = self.oauth.build_authorization_url(shop, user.id)
        return {"authorization_url": auth_url, "state": state, "shop_domain": shop}

    async def complete_connection(
        self,
        shop_domain: str,
        code: str,
        state: str,
        hmac_valid: bool = True,
    ) -> Store:
        """Complete OAuth callback and persist store credentials."""
        if not hmac_valid:
            raise ShopifyAuthError("Invalid OAuth callback HMAC", error_code="INVALID_HMAC")

        state_payload = self.oauth.verify_state_token(state)
        user_id = uuid.UUID(state_payload["sub"])
        shop = normalize_shop_domain(shop_domain)

        if state_payload.get("shop") != shop:
            raise ShopifyAuthError("OAuth state shop mismatch", error_code="SHOP_MISMATCH")

        token_data = await self.oauth.exchange_code_for_token(shop, code)

        store = await self.store_repo.get_by_shop_domain(shop)
        if store is None:
            store = Store(
                owner_id=user_id,
                shop_domain=shop,
                is_connected=False,
            )
            store = await self.store_repo.create(store)
        elif store.owner_id != user_id:
            raise ForbiddenError("Shop belongs to another user", error_code="SHOP_FORBIDDEN")

        client = ShopifyGraphQLClient(shop, token_data["access_token"], self.settings)
        shop_info = await client.get_shop_info()

        store.shop_name = shop_info.get("name")
        store.shopify_shop_id = shop_info.get("id")
        await self.token_manager.store_token(store, token_data["access_token"], token_data["scope"])

        logger.info("Shopify store connected: {} for user={}", shop, user_id)
        return store

    async def get_user_store(self, user: User) -> Store:
        """Return the connected store for a user."""
        stores = await self.store_repo.get_connected_by_owner_id(user.id)
        if not stores:
            raise NotFoundError("No connected Shopify store found", error_code="STORE_NOT_FOUND")
        return stores[0]

    async def disconnect_store(self, user: User) -> Store:
        """Disconnect the user's Shopify store."""
        store = await self.get_user_store(user)
        return await self.token_manager.revoke_token(store)

    async def trigger_sync(
        self,
        user: User,
        sync_type: SyncType = SyncType.FULL,
    ):
        """Trigger a manual sync for the user's connected store."""
        store = await self.get_user_store(user)
        if not store.is_connected:
            raise ShopifyAuthError("Store is not connected", error_code="STORE_NOT_CONNECTED")
        return await self.sync_engine.sync_store(store, sync_type, triggered_by="manual")
