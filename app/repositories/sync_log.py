import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_log import SyncLog, SyncLogStatus
from app.repositories.base import BaseRepository


class SyncLogRepository(BaseRepository[SyncLog]):
    model = SyncLog

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_log(
        self,
        store_id: uuid.UUID,
        sync_type: str,
        triggered_by: str = "manual",
    ) -> SyncLog:
        log = SyncLog(
            store_id=store_id,
            sync_type=sync_type,
            status=SyncLogStatus.RUNNING,
            started_at=datetime.now(UTC),
            triggered_by=triggered_by,
        )
        return await self.create(log)

    async def complete(
        self,
        log: SyncLog,
        records_processed: int,
        records_failed: int,
    ) -> SyncLog:
        log.status = SyncLogStatus.COMPLETED
        log.completed_at = datetime.now(UTC)
        log.records_processed = records_processed
        log.records_failed = records_failed
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def fail(self, log: SyncLog, error_message: str) -> SyncLog:
        log.status = SyncLogStatus.FAILED
        log.completed_at = datetime.now(UTC)
        log.error_message = error_message
        await self.session.flush()
        await self.session.refresh(log)
        return log
