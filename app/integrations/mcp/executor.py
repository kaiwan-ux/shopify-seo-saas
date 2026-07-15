"""Centralized MCP tool executor — the single execution layer for Phase 3 AI agents."""

import time
import uuid
from typing import Any

import httpx

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import IntegrationError, NotFoundError
from app.integrations.mcp.client import MCPClient
from app.integrations.mcp.config import MCPConfig
from app.integrations.mcp.registry import MCPToolRegistry
from app.integrations.shopify.graphql import ShopifyGraphQLClient
from app.integrations.shopify.sync import ShopifySyncEngine
from app.integrations.shopify.token_manager import ShopifyTokenManager
from app.models.mcp_tool_log import MCPToolLogStatus
from app.models.sync_log import SyncType
from app.repositories.collection import CollectionRepository
from app.repositories.mcp_tool_log import MCPToolLogRepository
from app.repositories.page import PageRepository
from app.repositories.product import ProductRepository
from app.repositories.store import StoreRepository


class MCPToolExecutor:
    """Executes MCP tools with retry, logging, and local fallbacks.

    Phase 3 AI agents MUST use this executor instead of calling MCP directly.
    """

    def __init__(self, session: AsyncSession, config: MCPConfig | None = None) -> None:
        self.session = session
        self.config = config or MCPConfig.from_settings()
        self.client = MCPClient(self.config)
        self.registry = MCPToolRegistry(self.config)
        self.log_repo = MCPToolLogRepository(session)
        self.store_repo = StoreRepository(session)
        self.product_repo = ProductRepository(session)
        self.collection_repo = CollectionRepository(session)
        self.page_repo = PageRepository(session)
        self.token_manager = ShopifyTokenManager(session)
        self.sync_engine = ShopifySyncEngine(session)

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        store_id: uuid.UUID | None = None,
        executed_by: str = "system",
    ) -> dict[str, Any]:
        """Execute a tool with full logging and error handling."""
        await self.registry.initialize()

        if not self.registry.has_tool(tool_name):
            raise NotFoundError(f"MCP tool '{tool_name}' not found", error_code="TOOL_NOT_FOUND")

        start = time.perf_counter()
        attempt = 1
        last_error: str | None = None

        while attempt <= self.config.max_retries:
            try:
                result = await self._dispatch(tool_name, arguments)
                duration_ms = int((time.perf_counter() - start) * 1000)

                await self.log_repo.create_log(
                    store_id=store_id or self._extract_store_id(arguments),
                    tool_name=tool_name,
                    arguments=arguments,
                    result=result,
                    status=MCPToolLogStatus.SUCCESS,
                    duration_ms=duration_ms,
                    attempt=attempt,
                    executed_by=executed_by,
                )

                logger.info(
                    "MCP tool executed: {} attempt={} duration={}ms",
                    tool_name,
                    attempt,
                    duration_ms,
                )
                return result

            except Exception as exc:
                last_error = str(exc)
                duration_ms = int((time.perf_counter() - start) * 1000)

                await self.log_repo.create_log(
                    store_id=store_id or self._extract_store_id(arguments),
                    tool_name=tool_name,
                    arguments=arguments,
                    status=MCPToolLogStatus.RETRY if attempt < self.config.max_retries else MCPToolLogStatus.FAILED,
                    duration_ms=duration_ms,
                    attempt=attempt,
                    error_message=last_error,
                    executed_by=executed_by,
                )

                if attempt >= self.config.max_retries:
                    logger.error("MCP tool {} failed after {} attempts: {}", tool_name, attempt, last_error)
                    raise IntegrationError(
                        f"Tool '{tool_name}' failed: {last_error}",
                        error_code="MCP_TOOL_EXECUTION_FAILED",
                    ) from exc

                attempt += 1
                logger.warning("MCP tool {} attempt {} failed, retrying: {}", tool_name, attempt - 1, last_error)

        raise IntegrationError(f"Tool '{tool_name}' exhausted retries", error_code="MCP_TOOL_EXHAUSTED")

    async def _dispatch(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route tool execution to local handler or remote MCP server."""
        local_handlers = {
            "get_products": self._handle_get_products,
            "get_collections": self._handle_get_collections,
            "get_pages": self._handle_get_pages,
            "update_product_seo": self._handle_update_product_seo,
            "update_collection_seo": self._handle_update_collection_seo,
            "update_product_content": self._handle_update_product_content,
            "update_collection_content": self._handle_update_collection_content,
            "update_page_content": self._handle_update_page_content,
            "sync_store": self._handle_sync_store,
        }

        if tool_name in local_handlers:
            return await local_handlers[tool_name](arguments)

        if self.client.is_available:
            return await self.client.call_tool(tool_name, arguments)

        raise IntegrationError(
            f"No handler for tool '{tool_name}' and MCP server unavailable",
            error_code="TOOL_UNAVAILABLE",
        )

    async def _handle_get_products(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        limit = arguments.get("limit", 25)
        products = await self.product_repo.list_by_store(store_id, limit=limit)
        return {
            "products": [
                {
                    "id": str(p.id),
                    "shopify_id": p.shopify_id,
                    "title": p.title,
                    "handle": p.handle,
                    "description": p.description,
                    "status": p.status,
                    "vendor": p.vendor,
                    "product_type": p.product_type,
                    "seo_title": p.seo_title,
                    "seo_description": p.seo_description,
                    "tags": p.tags or [],
                }
                for p in products
            ],
            "count": len(products),
        }

    async def _handle_get_collections(self, arguments: dict[str, Any]) -> dict[str, Any]:
        from app.repositories.collection import CollectionRepository

        store_id = uuid.UUID(arguments["store_id"])
        limit = arguments.get("limit", 25)
        repo = CollectionRepository(self.session)
        collections = await repo.list_by_store(store_id, limit=limit)
        return {
            "collections": [
                {
                    "id": str(c.id),
                    "shopify_id": c.shopify_id,
                    "title": c.title,
                    "handle": c.handle,
                    "description": c.description,
                    "seo_title": c.seo_title,
                    "seo_description": c.seo_description,
                    "products_count": c.products_count,
                }
                for c in collections
            ],
            "count": len(collections),
        }

    async def _handle_get_pages(self, arguments: dict[str, Any]) -> dict[str, Any]:
        from app.repositories.page import PageRepository

        store_id = uuid.UUID(arguments["store_id"])
        limit = arguments.get("limit", 25)
        repo = PageRepository(self.session)
        pages = await repo.list_by_store(store_id, limit=limit)
        return {
            "pages": [
                {
                    "id": str(p.id),
                    "shopify_id": p.shopify_id,
                    "title": p.title,
                    "handle": p.handle,
                    "body_html": p.body_html,
                    "seo_title": p.seo_title,
                    "seo_description": p.seo_description,
                    "is_published": p.is_published,
                }
                for p in pages
            ],
            "count": len(pages),
        }

    async def _resolve_product_shopify_id(self, store_id: uuid.UUID, raw_id: str) -> str:
        if raw_id.startswith("gid://shopify/Product/"):
            return raw_id

        product = None
        try:
            product = await self.product_repo.get_by_store_and_id(store_id, uuid.UUID(raw_id))
        except (TypeError, ValueError):
            product = None

        if product is None:
            product = await self.product_repo.get_by_store_and_shopify_id(store_id, raw_id)

        if product is not None:
            return product.shopify_id

        if raw_id.isdigit():
            return f"gid://shopify/Product/{raw_id}"

        raise IntegrationError(
            f"Cannot resolve product identifier '{raw_id}' to a Shopify product GID",
            error_code="SHOPIFY_PRODUCT_ID_NOT_RESOLVED",
        )

    async def _resolve_collection_shopify_id(self, store_id: uuid.UUID, raw_id: str) -> str:
        if raw_id.startswith("gid://shopify/Collection/"):
            return raw_id

        collection = None
        try:
            collection = await self.collection_repo.get_by_store_and_id(store_id, uuid.UUID(raw_id))
        except (TypeError, ValueError):
            collection = None

        if collection is None:
            collection = await self.collection_repo.get_by_store_and_shopify_id(store_id, raw_id)

        if collection is not None:
            return collection.shopify_id

        if raw_id.isdigit():
            return f"gid://shopify/Collection/{raw_id}"

        raise IntegrationError(
            f"Cannot resolve collection identifier '{raw_id}' to a Shopify collection GID",
            error_code="SHOPIFY_COLLECTION_ID_NOT_RESOLVED",
        )

    async def _resolve_page_shopify_id(self, store_id: uuid.UUID, raw_id: str) -> str:
        if raw_id.startswith("gid://shopify/Page/") or raw_id.startswith("gid://shopify/OnlineStorePage/"):
            return raw_id

        page = None
        try:
            page = await self.page_repo.get_by_store_and_id(store_id, uuid.UUID(raw_id))
        except (TypeError, ValueError):
            page = None

        if page is None:
            page = await self.page_repo.get_by_store_and_shopify_id(store_id, raw_id)

        if page is not None:
            return page.shopify_id

        if raw_id.isdigit():
            return f"gid://shopify/Page/{raw_id}"

        raise IntegrationError(
            f"Cannot resolve page identifier '{raw_id}' to a Shopify page GID",
            error_code="SHOPIFY_PAGE_ID_NOT_RESOLVED",
        )

    async def _handle_update_product_seo(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        store, token = await self.token_manager.get_access_token_by_store_id(store_id)
        client = ShopifyGraphQLClient(store.shop_domain, token)
        product_shopify_id = await self._resolve_product_shopify_id(
            store_id, str(arguments.get("product_shopify_id") or arguments.get("product_id") or "")
        )

        mutation = """
        mutation UpdateProductSEO($input: ProductInput!) {
          productUpdate(input: $input) {
            product { id title seo { title description } }
            userErrors { field message }
          }
        }
        """
        seo_input: dict[str, Any] = {"id": product_shopify_id}
        seo_fields: dict[str, str] = {}
        if "seo_title" in arguments:
            seo_fields["title"] = arguments["seo_title"]
        if "seo_description" in arguments:
            seo_fields["description"] = arguments["seo_description"]
        if seo_fields:
            seo_input["seo"] = seo_fields

        data = await client.execute(mutation, {"input": seo_input})
        result = data.get("productUpdate", {})
        if result.get("userErrors"):
            raise IntegrationError(
                f"Shopify SEO update failed: {result['userErrors']}",
                error_code="SHOPIFY_SEO_UPDATE_FAILED",
            )
        return {"product": result.get("product")}

    async def _handle_update_collection_seo(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        store, token = await self.token_manager.get_access_token_by_store_id(store_id)
        client = ShopifyGraphQLClient(store.shop_domain, token)
        collection_shopify_id = await self._resolve_collection_shopify_id(
            store_id, str(arguments.get("collection_shopify_id") or arguments.get("collection_id") or "")
        )

        mutation = """
        mutation UpdateCollectionSEO($input: CollectionInput!) {
          collectionUpdate(input: $input) {
            collection { id title seo { title description } }
            userErrors { field message }
          }
        }
        """
        seo_input: dict[str, Any] = {"id": collection_shopify_id}
        seo_fields: dict[str, str] = {}
        if "seo_title" in arguments:
            seo_fields["title"] = arguments["seo_title"]
        if "seo_description" in arguments:
            seo_fields["description"] = arguments["seo_description"]
        if seo_fields:
            seo_input["seo"] = seo_fields

        data = await client.execute(mutation, {"input": seo_input})
        result = data.get("collectionUpdate", {})
        if result.get("userErrors"):
            raise IntegrationError(
                f"Shopify collection SEO update failed: {result['userErrors']}",
                error_code="SHOPIFY_COLLECTION_SEO_UPDATE_FAILED",
            )
        return {"collection": result.get("collection")}

    async def _handle_update_product_content(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        store, token = await self.token_manager.get_access_token_by_store_id(store_id)
        client = ShopifyGraphQLClient(store.shop_domain, token)
        product_shopify_id = await self._resolve_product_shopify_id(
            store_id, str(arguments.get("product_shopify_id") or arguments.get("product_id") or "")
        )

        mutation = """
        mutation UpdateProductContent($input: ProductInput!) {
          productUpdate(input: $input) {
            product { id title descriptionHtml }
            userErrors { field message }
          }
        }
        """
        product_input = {
            "id": product_shopify_id,
            "descriptionHtml": arguments.get("description_html", ""),
        }
        data = await client.execute(mutation, {"input": product_input})
        result = data.get("productUpdate", {})
        if result.get("userErrors"):
            raise IntegrationError(
                f"Shopify product content update failed: {result['userErrors']}",
                error_code="SHOPIFY_PRODUCT_CONTENT_UPDATE_FAILED",
            )
        return {"product": result.get("product")}

    async def _handle_update_collection_content(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        store, token = await self.token_manager.get_access_token_by_store_id(store_id)
        client = ShopifyGraphQLClient(store.shop_domain, token)
        collection_shopify_id = await self._resolve_collection_shopify_id(
            store_id, str(arguments.get("collection_shopify_id") or arguments.get("collection_id") or "")
        )

        mutation = """
        mutation UpdateCollectionContent($input: CollectionInput!) {
          collectionUpdate(input: $input) {
            collection { id title descriptionHtml }
            userErrors { field message }
          }
        }
        """
        collection_input = {
            "id": collection_shopify_id,
            "descriptionHtml": arguments.get("description_html", ""),
        }
        data = await client.execute(mutation, {"input": collection_input})
        result = data.get("collectionUpdate", {})
        if result.get("userErrors"):
            raise IntegrationError(
                f"Shopify collection content update failed: {result['userErrors']}",
                error_code="SHOPIFY_COLLECTION_CONTENT_UPDATE_FAILED",
            )
        return {"collection": result.get("collection")}

    async def _handle_update_page_content(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        store, token = await self.token_manager.get_access_token_by_store_id(store_id)
        page_shopify_id = await self._resolve_page_shopify_id(
            store_id, str(arguments.get("page_shopify_id") or arguments.get("page_id") or "")
        )
        numeric_id = _shopify_numeric_id(page_shopify_id)
        url = f"https://{store.shop_domain}/admin/api/{self.sync_engine.settings.shopify_api_version}/pages/{numeric_id}.json"
        payload = {"page": {"id": int(numeric_id), "body_html": arguments.get("description_html", "")}}
        headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.put(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise IntegrationError(
                f"Shopify page content update failed HTTP {response.status_code}: {response.text[:300]}",
                error_code="SHOPIFY_PAGE_CONTENT_UPDATE_FAILED",
            )
        return {"page": response.json().get("page")}

    async def _handle_sync_store(self, arguments: dict[str, Any]) -> dict[str, Any]:
        store_id = uuid.UUID(arguments["store_id"])
        sync_type_str = arguments.get("sync_type", "full")
        sync_type = SyncType(sync_type_str)

        store = await self.store_repo.get_by_id(store_id)
        if store is None:
            raise NotFoundError("Store not found")

        sync_log = await self.sync_engine.sync_store(store, sync_type, triggered_by="mcp_tool")
        return {
            "sync_log_id": str(sync_log.id),
            "status": sync_log.status,
            "records_processed": sync_log.records_processed,
        }

    @staticmethod
    def _extract_store_id(arguments: dict[str, Any]) -> uuid.UUID | None:
        raw = arguments.get("store_id")
        if raw:
            return uuid.UUID(str(raw))
        return None


def _shopify_numeric_id(shopify_id: str) -> str:
    value = str(shopify_id or "").rstrip("/")
    numeric = value.split("/")[-1]
    if not numeric.isdigit():
        raise IntegrationError(
            f"Cannot extract numeric Shopify ID from '{shopify_id}'",
            error_code="SHOPIFY_NUMERIC_ID_NOT_RESOLVED",
        )
    return numeric
