"""Auto Fix Agent â€” execute approved fixes via tool layer."""

import uuid

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction


class AutoFixAgent(BaseAgent):
    name = AgentName.AUTOFIX

    async def _execute(self, context: AgentContext) -> AgentOutput:
        content_output = context.agent_outputs.get("content")
        approved = content_output.result.get("optimizations", []) if content_output else []

        executed: list[dict] = []
        failed: list[dict] = []

        for fix in _merge_seo_fixes(approved):
            field = fix.get("field")
            resource_type = fix.get("resource_type", "product")
            if field not in ("seo", "seo_title", "seo_description", "title", "description", "description_html"):
                failed.append({"fix": fix, "status": "failed", "error": f"Unsupported field: {field}"})
                continue
            if resource_type == "page" and field != "description_html":
                failed.append({
                    "fix": fix,
                    "status": "failed",
                    "error": "Page SEO title/meta writes are advisory-only; automatic page writes are limited to body content.",
                })
                continue
            if resource_type not in ("product", "collection", "page"):
                failed.append({"fix": fix, "status": "failed", "error": f"Unsupported resource type: {resource_type}"})
                continue

            try:
                id_key = "product_shopify_id" if resource_type == "product" else "collection_shopify_id" if resource_type == "collection" else "page_shopify_id"
                if field == "description_html":
                    tool_name = "update_product_content" if resource_type == "product" else "update_collection_content" if resource_type == "collection" else "update_page_content"
                    args: dict = {
                        "store_id": context.store_id,
                        id_key: fix.get("resource_id", ""),
                        "description_html": fix.get("suggested_value", ""),
                    }
                else:
                    tool_name = "update_product_seo" if resource_type == "product" else "update_collection_seo"
                    args = {
                        "store_id": context.store_id,
                        id_key: fix.get("resource_id", ""),
                    }
                    if field == "seo":
                        suggested = fix.get("suggested_value", {}) or {}
                        if suggested.get("seo_title"):
                            args["seo_title"] = suggested.get("seo_title")
                        if suggested.get("seo_description"):
                            args["seo_description"] = suggested.get("seo_description")
                    else:
                        if "seo_title" in str(field) or field == "title":
                            args["seo_title"] = fix.get("suggested_value", "")
                        if "seo_description" in str(field) or field == "description":
                            args["seo_description"] = fix.get("suggested_value", "")

                result = await self.tools.execute(
                    tool_name,
                    args,
                    store_id=uuid.UUID(context.store_id),
                    agent_name=self.name,
                )
                executed.append({"fix": fix, "status": "success", "result": result})
            except Exception as exc:
                failed.append({"fix": fix, "status": "failed", "error": str(exc)})

        return AgentOutput(
            agent_name=self.name,
            reasoning=f"Executed {len(executed)} fixes, {len(failed)} failed",
            result={"executed": executed, "failed": failed, "summary": f"{len(executed)} applied"},
            confidence=0.9 if not failed else 0.6,
            next_action=NextAction.CONTINUE,
            required_tools=["update_product_seo", "update_collection_seo", "update_product_content", "update_collection_content", "update_page_content"],
        )


def _merge_seo_fixes(fixes: list[dict]) -> list[dict]:
    """Combine SEO title/description fixes per resource before writing to Shopify.

    Shopify treats the nested seo payload as a single object on update. Sending
    title and description in separate calls can leave the other value null after
    a later write, so approvals must be merged into one safe tool execution.
    """
    merged: dict[tuple[str, str], dict] = {}
    result: list[dict] = []

    for fix in fixes:
        field = fix.get("field")
        resource_type = str(fix.get("resource_type", "product"))
        if resource_type in {"product", "collection"} and field in {"seo_title", "seo_description", "title", "description"}:
            key = (resource_type, str(fix.get("resource_id", "")))
            current = merged.get(key)
            if current is None:
                current = {**fix, "field": "seo", "suggested_value": {}, "current_value": {}}
                merged[key] = current
                result.append(current)
            suggested = dict(current.get("suggested_value") or {})
            current_value = dict(current.get("current_value") or {})
            target_field = "seo_title" if field in {"seo_title", "title"} else "seo_description"
            suggested[target_field] = fix.get("suggested_value", "")
            current_value[target_field] = fix.get("current_value")
            current["suggested_value"] = suggested
            current["current_value"] = current_value
            current["confidence"] = min(float(current.get("confidence", 1.0)), float(fix.get("confidence", 1.0)))
            current["reason"] = "Apply SEO title and meta description together so Shopify does not clear one field."
        else:
            result.append(fix)
    return result

