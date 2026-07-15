import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_log import WebhookLog, WebhookLogStatus
from app.repositories.base import BaseRepository


class WebhookLogRepository(BaseRepository[WebhookLog]):
    model = WebhookLog

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_log(
        self,
        topic: str,
        shop_domain: str,
        store_id: uuid.UUID | None = None,
        shopify_webhook_id: str | None = None,
        payload_hash: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> WebhookLog:
        log = WebhookLog(
            store_id=store_id,
            topic=topic,
            shop_domain=shop_domain,
            shopify_webhook_id=shopify_webhook_id,
            payload_hash=payload_hash,
            payload=payload,
            status=WebhookLogStatus.RECEIVED,
        )
        return await self.create(log)

    async def update_status(
        self,
        log: WebhookLog,
        status: WebhookLogStatus,
        error_message: str | None = None,
    ) -> WebhookLog:
        log.status = status.value if hasattr(status, "value") else status
        log.processed_at = datetime.now(UTC)
        if error_message:
            log.error_message = error_message
        await self.session.flush()
        await self.session.refresh(log)
        return log
