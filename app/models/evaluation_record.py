"""AI evaluation results."""

import uuid
from enum import StrEnum

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class EvaluationType(StrEnum):
    JSON_VALIDITY = "json_validity"
    TOOL_SELECTION = "tool_selection"
    EXECUTION_SUCCESS = "execution_success"
    AGENT_ACCURACY = "agent_accuracy"
    WORKFLOW_CORRECTNESS = "workflow_correctness"
    HALLUCINATION = "hallucination"


class EvaluationRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Automated evaluation of agent/workflow outputs."""

    __tablename__ = "evaluation_records"

    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    evaluation_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target: Mapped[str] = mapped_column(String(128), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool] = mapped_column(default=False, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<EvaluationRecord type={self.evaluation_type} passed={self.passed}>"
