"""Tests for AI infrastructure."""

import pytest

from app.agents.shared.registry import list_agents
from app.policies.approval import ApprovalPolicy


def test_list_agents():
    agents = list_agents()
    assert len(agents) == 8
    names = {a["name"] for a in agents}
    assert "planner" in names
    assert "audit" in names
    assert "autofix" in names


def test_approval_policy_safe_actions():
    policy = ApprovalPolicy()
    assert policy.classify("get_products").requires_approval is False
    assert policy.classify("get_products").risk.value == "safe"


def test_approval_policy_dangerous_actions(test_settings):
    policy = ApprovalPolicy()
    result = policy.classify("update_product_seo")
    assert result.requires_approval is True
    assert result.risk.value == "dangerous"


def test_prompt_manager_loads_templates():
    from app.prompts.manager import PromptManager

    manager = PromptManager()
    templates = manager.load_all_templates()
    assert "planner" in templates
    assert "audit" in templates
    system, _ = manager.render("planner", {"store_id": "test", "task": "audit my store"})
    assert "Planner Agent" in system


def test_autofix_merges_seo_title_and_description():
    from app.agents.autofix.agent import _merge_seo_fixes

    fixes = [
        {"resource_id": "product-1", "resource_type": "product", "field": "seo_title", "suggested_value": "Snowboard | Brand", "confidence": 0.9},
        {"resource_id": "product-1", "resource_type": "product", "field": "seo_description", "suggested_value": "Useful snowboard description for search results.", "confidence": 0.8},
        {"resource_id": "product-1", "resource_type": "product", "field": "description_html", "suggested_value": "<p>Body</p>", "confidence": 0.7},
    ]

    merged = _merge_seo_fixes(fixes)

    assert len(merged) == 2
    assert merged[0]["field"] == "seo"
    assert merged[0]["suggested_value"] == {
        "seo_title": "Snowboard | Brand",
        "seo_description": "Useful snowboard description for search results.",
    }
    assert merged[1]["field"] == "description_html"
