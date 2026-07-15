"""Approval policies for AI agent actions."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel

class ActionRisk(StrEnum):
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"


class ActionClassification(BaseModel):
    action_type: str
    risk: ActionRisk
    requires_approval: bool
    reason: str


SAFE_ACTIONS = {
    "get_products", "get_collections", "get_pages", "sync_store",
    "read_audit", "generate_report", "analyze",
}

MODERATE_ACTIONS = {
    "sync_store",
}

DANGEROUS_ACTIONS = {
    "update_product_seo", "update_page_seo", "create_redirect",
    "delete_redirect", "bulk_update",
}


class ApprovalPolicy:
    """Determines whether an agent action requires human approval."""

    def classify(self, action_type: str) -> ActionClassification:
        if action_type in DANGEROUS_ACTIONS:
            return ActionClassification(
                action_type=action_type,
                risk=ActionRisk.DANGEROUS,
                requires_approval=True,
                reason="Write operation that modifies store data",
            )

        if action_type in MODERATE_ACTIONS:
            return ActionClassification(
                action_type=action_type,
                risk=ActionRisk.MODERATE,
                requires_approval=False,
                reason="Sync operation — safe but resource-intensive",
            )

        return ActionClassification(
            action_type=action_type,
            risk=ActionRisk.SAFE,
            requires_approval=False,
            reason="Read-only operation",
        )

    def classify_tool(self, tool_name: str) -> ActionClassification:
        return self.classify(tool_name)

    def requires_approval_for_fixes(self, fixes: list[dict[str, Any]]) -> bool:
        """Check if a list of proposed fixes requires approval.

        Content agents emit proposed changes, not executable tool calls. Treat
        explicit approval flags and Shopify SEO field edits as approval-gated so
        generated metadata cannot be auto-published accidentally.
        """
        write_fields = {"seo_title", "seo_description", "title", "description"}
        for fix in fixes:
            if fix.get("approval_required") is True:
                return True
            tool = fix.get("tool", fix.get("action_type", ""))
            if tool and self.classify(tool).requires_approval:
                return True
            if fix.get("resource_type") == "product" and fix.get("field") in write_fields:
                return True
        return False
