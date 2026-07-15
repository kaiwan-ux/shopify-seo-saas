"""Shopify webhook signature verification and event processing."""

import base64
import hashlib
import hmac
import json
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.exceptions import WebhookVerificationError
from app.integrations.shopify.sync import ShopifySyncEngine
from app.integrations.shopify.token_manager import ShopifyTokenManager
from app.models.webhook_log import WebhookLogStatus
from app.repositories.store import StoreRepository
from app.repositories.webhook_log import WebhookLogRepository

SUPPORTED_TOPICS = {
    "products/create",
    "products/update",
    "products/delete",
    "collections/update",
    "app/uninstalled",
    "inventory_levels/update",
}


class ShopifyWebhookHandler:
    """Verifies and processes incoming Shopify webhooks."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.store_repo = StoreRepository(session)
        self.webhook_log_repo = WebhookLogRepository(session)
        self.token_manager = ShopifyTokenManager(session)
        self.sync_engine = ShopifySyncEngine(session, self.settings)

    def verify_signature(self, body: bytes, hmac_header: str | None) -> bool:
        """Verify Shopify webhook HMAC-SHA256 signature (base64-encoded)."""
        if not hmac_header:
            return False

        digest = hmac.new(
            self.settings.shopify_api_secret.encode(),
            body,
            hashlib.sha256,
        ).digest()
        computed = base64.b64encode(digest)

        return hmac.compare_digest(computed, hmac_header.encode("utf-8"))

    async def handle(
        self,
        topic: str,
        shop_domain: str,
        body: bytes,
        hmac_header: str | None,
        webhook_id: str | None = None,
    ) -> dict[str, str]:
        """Process a verified webhook event."""
        if not self.verify_signature(body, hmac_header):
            raise WebhookVerificationError()

        payload: dict[str, Any] = json.loads(body)
        payload_hash = hashlib.sha256(body).hexdigest()

        store = await self.store_repo.get_by_shop_domain(shop_domain)
        log = await self.webhook_log_repo.create_log(
            topic=topic,
            shop_domain=shop_domain,
            store_id=store.id if store else None,
            shopify_webhook_id=webhook_id,
            payload_hash=payload_hash,
            payload=payload,
        )

        if topic not in SUPPORTED_TOPICS:
            await self.webhook_log_repo.update_status(log, WebhookLogStatus.IGNORED)
            return {"status": "ignored", "topic": topic}

        try:
            await self._dispatch(topic, store, payload)
            await self.webhook_log_repo.update_status(log, WebhookLogStatus.PROCESSED)
            return {"status": "processed", "topic": topic}
        except Exception as exc:
            await self.webhook_log_repo.update_status(
                log, WebhookLogStatus.FAILED, error_message=str(exc)
            )
            logger.exception("Webhook processing failed topic={} shop={}", topic, shop_domain)
            raise

    async def _dispatch(
        self,
        topic: str,
        store: Any,
        payload: dict[str, Any],
    ) -> None:
        if store is None:
            logger.warning("Webhook for unknown store topic={}", topic)
            return

        if topic == "app/uninstalled":
            await self.token_manager.revoke_token(store)
            return

        if topic in ("products/create", "products/update"):
            shopify_id = f"gid://shopify/Product/{payload.get('id')}"
            await self.sync_engine._upsert_product(store, {
                "id": shopify_id,
                "title": payload.get("title", ""),
                "handle": payload.get("handle", ""),
                "descriptionHtml": payload.get("body_html"),
                "status": payload.get("status"),
                "vendor": payload.get("vendor"),
                "productType": payload.get("product_type"),
                "tags": payload.get("tags", []),
                "seo": {},
            })
            return

        if topic == "products/delete":
            shopify_id = f"gid://shopify/Product/{payload.get('id')}"
            await self.sync_engine.mark_product_deleted(store, shopify_id)
            return

        if topic == "collections/update":
            shopify_id = f"gid://shopify/Collection/{payload.get('id')}"
            await self.sync_engine._upsert_collection(store, {
                "id": shopify_id,
                "title": payload.get("title", ""),
                "handle": payload.get("handle", ""),
                "descriptionHtml": payload.get("body_html"),
                "seo": {},
                "productsCount": {"count": None},
            })
            return

        if topic == "inventory_levels/update":
            logger.info("Inventory update webhook received for store={}", store.shop_domain)
            return

        logger.info("Unhandled webhook topic={} for store={}", topic, store.shop_domain)
