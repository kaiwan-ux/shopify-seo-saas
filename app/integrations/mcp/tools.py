"""Known Shopify MCP tool definitions for Phase 3 agent consumption."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MCPToolDefinition:
    """Metadata for a registered MCP tool."""

    name: str
    description: str
    input_schema: dict
    category: str = "shopify"


SHOPIFY_MCP_TOOLS: list[MCPToolDefinition] = [
    MCPToolDefinition(
        name="get_products",
        description="Fetch products from a connected Shopify store",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string", "description": "Internal store UUID"},
                "limit": {"type": "integer", "default": 25},
                "query": {"type": "string", "description": "Search query filter"},
            },
            "required": ["store_id"],
        },
        category="catalog",
    ),
    MCPToolDefinition(
        name="get_collections",
        description="Fetch collections from a connected Shopify store",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "limit": {"type": "integer", "default": 25},
            },
            "required": ["store_id"],
        },
        category="catalog",
    ),
    MCPToolDefinition(
        name="get_pages",
        description="Fetch online store pages from Shopify",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "limit": {"type": "integer", "default": 25},
            },
            "required": ["store_id"],
        },
        category="content",
    ),
    MCPToolDefinition(
        name="update_product_seo",
        description="Update SEO title and description for a Shopify product",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "product_shopify_id": {"type": "string"},
                "seo_title": {"type": "string"},
                "seo_description": {"type": "string"},
            },
            "required": ["store_id", "product_shopify_id"],
        },
        category="seo",
    ),
    MCPToolDefinition(
        name="update_collection_seo",
        description="Update SEO title and description for a Shopify collection",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "collection_shopify_id": {"type": "string"},
                "seo_title": {"type": "string"},
                "seo_description": {"type": "string"},
            },
            "required": ["store_id", "collection_shopify_id"],
        },
        category="seo",
    ),
    MCPToolDefinition(
        name="update_product_content",
        description="Update the body description HTML for a Shopify product",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "product_shopify_id": {"type": "string"},
                "description_html": {"type": "string"},
            },
            "required": ["store_id", "product_shopify_id", "description_html"],
        },
        category="content",
    ),
    MCPToolDefinition(
        name="update_collection_content",
        description="Update the body description HTML for a Shopify collection",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "collection_shopify_id": {"type": "string"},
                "description_html": {"type": "string"},
            },
            "required": ["store_id", "collection_shopify_id", "description_html"],
        },
        category="content",
    ),
    MCPToolDefinition(
        name="update_page_content",
        description="Update the body HTML for a Shopify online store page",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "page_shopify_id": {"type": "string"},
                "description_html": {"type": "string"},
            },
            "required": ["store_id", "page_shopify_id", "description_html"],
        },
        category="content",
    ),
    MCPToolDefinition(
        name="sync_store",
        description="Trigger a full or partial store synchronization",
        input_schema={
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "sync_type": {
                    "type": "string",
                    "enum": ["full", "products", "collections", "pages", "blogs", "redirects"],
                },
            },
            "required": ["store_id"],
        },
        category="sync",
    ),
]
