"""Scheduled store synchronization jobs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import select

from app.config.settings import get_settings
from app.db.session import async_session_factory
from app.integrations.shopify.sync import ShopifySyncEngine
from app.models.store import Store
from app.models.sync_log import SyncType

_scheduler: AsyncIOScheduler | None = None


async def _run_scheduled_sync() -> None:
    """Sync all connected stores on schedule."""
    settings = get_settings()
    if not settings.sync_enabled:
        return

    logger.info("Starting scheduled sync for all connected stores")

    async with async_session_factory() as session:
        result = await session.execute(
            select(Store).where(Store.is_connected.is_(True))
        )
        stores = list(result.scalars().all())

        engine = ShopifySyncEngine(session, settings)
        for store in stores:
            try:
                await engine.sync_store(store, SyncType.FULL, triggered_by="scheduler")
                await session.commit()
                logger.info("Scheduled sync completed for store={}", store.shop_domain)
            except Exception as exc:
                await session.rollback()
                logger.error("Scheduled sync failed for store={}: {}", store.shop_domain, exc)


def start_scheduler() -> AsyncIOScheduler:
    """Start the background sync scheduler."""
    global _scheduler
    settings = get_settings()

    if not settings.sync_enabled:
        logger.info("Scheduled sync is disabled")
        return AsyncIOScheduler()

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _run_scheduled_sync,
        trigger="interval",
        hours=settings.sync_interval_hours,
        id="shopify_scheduled_sync",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Sync scheduler started — interval={}h",
        settings.sync_interval_hours,
    )
    return _scheduler


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Sync scheduler stopped")
    _scheduler = None
