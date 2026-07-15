"""LangGraph shared workflow state."""

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """Strongly typed shared state for the SEO workflow graph."""

    # Identity
    workflow_id: str
    user_id: str
    store_id: str
    task: str

    # Status
    status: str
    current_agent: str | None
    approval_status: str

    # Planner
    execution_plan: dict[str, Any] | None
    execution_order: list[str]
    current_step: int

    # Agent outputs (structured)
    agent_outputs: dict[str, dict[str, Any]]

    # Tool outputs
    tool_outputs: list[dict[str, Any]]

    # Approval
    pending_approvals: list[dict[str, Any]]
    approved_fixes: list[dict[str, Any]]

    # Errors & retries
    errors: list[dict[str, str]]
    retry_count: int
    max_retries: int

    # Observability
    logs: list[str]
    total_tokens: int

    # Final
    report: dict[str, Any] | None
