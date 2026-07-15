"""Shared agent communication models — agents NEVER exchange raw text."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentName(StrEnum):
    PLANNER = "planner"
    AUDIT = "audit"
    CONTENT = "content"
    TECHNICAL = "technical"
    PERFORMANCE = "performance"
    AUTOFIX = "autofix"
    MONITORING = "monitoring"
    REPORTING = "reporting"


class NextAction(StrEnum):
    CONTINUE = "continue"
    RETRY = "retry"
    STOP = "stop"
    AWAIT_APPROVAL = "await_approval"
    BRANCH = "branch"
    COMPLETE = "complete"


class AgentOutput(BaseModel):
    """Structured output every agent must return."""

    agent_name: str
    reasoning: str
    result: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    next_action: NextAction = NextAction.CONTINUE
    required_tools: list[str] = Field(default_factory=list)


class AgentContext(BaseModel):
    """Runtime context passed to every agent."""

    workflow_id: str
    user_id: str
    store_id: str
    task: str
    agent_outputs: dict[str, AgentOutput] = Field(default_factory=dict)
    rag_context: str = ""
    store_data: dict[str, Any] = Field(default_factory=dict)
