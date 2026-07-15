import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_record import EvaluationRecord
from app.repositories.base import BaseRepository


class EvaluationRepository(BaseRepository[EvaluationRecord]):
    model = EvaluationRecord

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        evaluation_type: str,
        target: str,
        passed: bool,
        workflow_run_id: uuid.UUID | None = None,
        agent_run_id: uuid.UUID | None = None,
        score: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> EvaluationRecord:
        record = EvaluationRecord(
            workflow_run_id=workflow_run_id,
            agent_run_id=agent_run_id,
            evaluation_type=evaluation_type,
            target=target,
            score=score,
            passed=passed,
            details=details,
        )
        return await super().create(record)

    async def list_by_workflow(self, workflow_run_id: uuid.UUID) -> list[EvaluationRecord]:
        result = await self.session.execute(
            select(EvaluationRecord)
            .where(EvaluationRecord.workflow_run_id == workflow_run_id)
            .order_by(EvaluationRecord.created_at)
        )
        return list(result.scalars().all())
