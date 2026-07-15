"""Content Optimization Agent ? generates high-impact Shopify SEO fixes."""

from app.agents.shared.base import BaseAgent
from app.agents.shared.models import AgentContext, AgentName, AgentOutput, NextAction
from app.intelligence.adapters import resources_from_store_data
from app.intelligence.metadata import MetadataIntelligenceEngine
from app.intelligence.utils import strip_html, words
from app.schemas.seo import MetadataRequest, ResourceType


class ContentAgent(BaseAgent):
    name = AgentName.CONTENT

    async def _execute(self, context: AgentContext) -> AgentOutput:
        store_data = context.store_data or await self._fetch_store_data(context.store_id)
        resources = resources_from_store_data(store_data)
        generator = MetadataIntelligenceEngine()
        optimizations = []

        for resource in resources:
            if resource.resource_type != ResourceType.PAGE:
                metadata = await generator.generate(MetadataRequest(resource=resource))
                if (resource.seo_title or "").strip() != metadata.seo_title.strip():
                    optimizations.append(
                        _fix(
                            resource,
                            "seo_title",
                            resource.seo_title,
                            metadata.seo_title,
                            metadata.confidence,
                            "Create a distinct 30-60 character search title.",
                        )
                    )
                if (resource.meta_description or "").strip() != metadata.meta_description.strip():
                    optimizations.append(
                        _fix(
                            resource,
                            "seo_description",
                            resource.meta_description,
                            metadata.meta_description,
                            metadata.confidence,
                            "Create a persuasive 120-160 character search snippet.",
                        )
                    )

            content_fix = _content_fix_for_resource(resource)
            if content_fix:
                optimizations.append(content_fix)

        confidence = (
            sum(item["confidence"] for item in optimizations) / len(optimizations)
            if optimizations
            else 0.8
        )
        return AgentOutput(
            agent_name=self.name,
            reasoning=f"Generated {len(optimizations)} metadata and content optimizations",
            result={"optimizations": optimizations, "resources_analyzed": len(resources)},
            confidence=confidence,
            next_action=NextAction.AWAIT_APPROVAL if optimizations else NextAction.CONTINUE,
            required_tools=["get_products", "get_collections", "get_pages"],
        )


def _fix(resource, field: str, current, suggested: str, confidence: float, reason: str) -> dict:
    return {
        "resource_id": resource.id,
        "resource_type": resource.resource_type.value,
        "field": field,
        "current_value": current,
        "suggested_value": suggested,
        "confidence": confidence,
        "approval_required": True,
        "reason": reason,
    }


def _content_fix_for_resource(resource) -> dict | None:
    current_text = strip_html(resource.body)
    minimum_words = 120 if resource.resource_type == ResourceType.PRODUCT else 170
    if len(words(current_text)) >= minimum_words:
        return None

    if resource.resource_type == ResourceType.PRODUCT:
        suggested = _product_description(resource)
        reason = "Add useful product copy to reduce thin-content findings and improve search relevance."
    elif resource.resource_type == ResourceType.COLLECTION:
        suggested = _collection_description(resource)
        reason = "Add collection copy to explain the category, internal relevance, and shopping intent."
    elif resource.resource_type == ResourceType.PAGE:
        suggested = _page_description(resource)
        reason = "Add useful page copy to reduce thin-content findings. Page SEO title/meta fields are advisory-only because Shopify does not expose them safely here."
    else:
        return None

    return _fix(resource, "description_html", resource.body, suggested, 0.78, reason)


def _product_description(resource) -> str:
    title = resource.title.strip()
    vendor = str(resource.metadata.get("vendor") or "").strip() if resource.metadata else ""
    product_type = str(resource.metadata.get("product_type") or "snowboard gear").strip() if resource.metadata else "snowboard gear"
    brand_phrase = f" from {vendor}" if vendor and vendor.lower() not in title.lower() else ""
    return (
        f"<p><strong>{title}</strong>{brand_phrase} is built for shoppers who want dependable {product_type} "
        "with clear details before they buy. This page explains the product in practical language so customers can "
        "compare options, understand the main use case, and decide whether it fits their riding style, budget, and "
        "everyday needs.</p>"
        f"<p>{title} helps your catalog page answer common buying questions instead of relying only on a short name or "
        "variant list. Review the available specifications, inventory, price, and product options before checkout, then "
        "consider compatible accessories or related snowboarding essentials for a complete setup.</p>"
        "<p>This description is written to support both shoppers and search engines with useful, unique copy. Keep it "
        "accurate, update it when product details change, and add more specific material, sizing, care, or performance "
        "details whenever they are available.</p>"
    )
def _collection_description(resource) -> str:
    title = resource.title.strip()
    count = resource.metadata.get("products_count") if resource.metadata else None
    count_phrase = f" Browse {count} selected products" if count else " Browse selected products"
    return (
        f"<p><strong>{title}</strong> brings together relevant products for shoppers who want a focused way to explore "
        "your catalog. This collection gives customers a clearer path from browsing to purchase by explaining what the "
        "category includes, why the products belong together, and how they can compare available choices.</p>"
        f"<p>{count_phrase} in this collection, review the available styles and details, and choose the item that best "
        "matches your needs. This page can also support stronger internal navigation by connecting shoppers with related "
        "gear, accessories, and product pages that answer the next question in their buying journey.</p>"
        f"<p>Use the {title} collection as a helpful landing page, not just a product grid. Add seasonal notes, buying "
        "guidance, fit considerations, material details, or merchandising context when available so customers and search "
        "engines both understand the value of the collection.</p>"
    )
def _page_description(resource) -> str:
    title = resource.title.strip()
    return (
        f"<p><strong>{title}</strong> gives shoppers clear information about this store page and helps them understand "
        "the next step. This content should answer common questions, explain the purpose of the page, and provide enough "
        "context for both customers and search engines to understand why the page exists.</p>"
        f"<p>Use the {title} page to communicate important details in plain language. Keep the copy accurate, helpful, "
        "and specific to your store. Add relevant links, contact details, policy notes, service information, or supporting "
        "guidance where appropriate so visitors can complete their task without confusion.</p>"
        "<p>Review this page after every major store update. Strong informational pages reduce uncertainty, improve trust, "
        "and give search engines more useful context than an empty or very short page can provide.</p>"
    )

