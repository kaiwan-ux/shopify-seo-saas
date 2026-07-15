"""Shopify store data synchronization engine."""

from datetime import UTC, datetime
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.exceptions import ShopifyPermissionError
from app.integrations.shopify.graphql import ShopifyGraphQLClient
from app.integrations.shopify.token_manager import ShopifyTokenManager
from app.models.store import Store, SyncStatus
from app.models.sync_log import SyncLog, SyncLogStatus, SyncType
from app.repositories.blog import BlogRepository
from app.repositories.collection import CollectionRepository
from app.repositories.page import PageRepository
from app.repositories.product import ProductRepository
from app.repositories.redirect import RedirectRepository
from app.repositories.sync_log import SyncLogRepository

PRODUCTS_QUERY = """
query Products($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    edges {
      node {
        id title handle descriptionHtml status vendor productType tags
        seo { title description }
      }
    }
  }
}
"""

COLLECTIONS_QUERY = """
query Collections($first: Int!, $after: String) {
  collections(first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    edges {
      node {
        id title handle descriptionHtml
        seo { title description }
        productsCount { count }
      }
    }
  }
}
"""

PAGES_QUERY = """
query Pages($first: Int!, $after: String) {
  pages(first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    edges {
      node {
        id title handle body isPublished
      }
    }
  }
}
"""

BLOGS_QUERY = """
query Blogs($first: Int!, $after: String) {
  blogs(first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    edges {
      node {
        id title handle
        articlesCount { count }
      }
    }
  }
}
"""

REDIRECTS_QUERY = """
query UrlRedirects($first: Int!, $after: String) {
  urlRedirects(first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    edges {
      node { id path target }
    }
  }
}
"""


class ShopifySyncEngine:
    """Synchronizes Shopify store data into the local database."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.token_manager = ShopifyTokenManager(session)
        self.sync_log_repo = SyncLogRepository(session)
        self.product_repo = ProductRepository(session)
        self.collection_repo = CollectionRepository(session)
        self.page_repo = PageRepository(session)
        self.blog_repo = BlogRepository(session)
        self.redirect_repo = RedirectRepository(session)

    async def sync_store(
        self,
        store: Store,
        sync_type: SyncType = SyncType.FULL,
        triggered_by: str = "manual",
    ) -> SyncLog:
        """Run a full or partial sync for a connected store."""
        sync_log = await self.sync_log_repo.create_log(
            store_id=store.id,
            sync_type=sync_type.value,
            triggered_by=triggered_by,
        )

        store.sync_status = SyncStatus.SYNCING
        await self.session.flush()

        try:
            access_token = await self.token_manager.get_access_token(store)
            client = ShopifyGraphQLClient(store.shop_domain, access_token, self.settings)
            total_processed = 0
            total_failed = 0

            sync_targets = self._resolve_sync_targets(sync_type)
            for target in sync_targets:
                processed, failed = await self._sync_resource(client, store, target)
                total_processed += processed
                total_failed += failed

            store.sync_status = SyncStatus.IDLE
            store.last_sync_at = datetime.now(UTC)
            store.last_sync_error = None

            await self.sync_log_repo.complete(
                sync_log,
                records_processed=total_processed,
                records_failed=total_failed,
            )
            logger.info(
                "Sync completed for store={} type={} processed={} failed={}",
                store.shop_domain,
                sync_type,
                total_processed,
                total_failed,
            )
            return sync_log

        except Exception as exc:
            store.sync_status = SyncStatus.ERROR
            store.last_sync_error = str(exc)
            await self.sync_log_repo.fail(sync_log, str(exc))
            logger.exception("Sync failed for store={}: {}", store.shop_domain, exc)
            raise

    def _resolve_sync_targets(self, sync_type: SyncType) -> list[str]:
        if sync_type == SyncType.FULL:
            return ["products", "collections", "pages", "blogs", "redirects"]
        return [sync_type.value]

    async def _sync_resource(
        self,
        client: ShopifyGraphQLClient,
        store: Store,
        resource: str,
    ) -> tuple[int, int]:
        query_map = {
            "products": (PRODUCTS_QUERY, "products", self._upsert_product),
            "collections": (COLLECTIONS_QUERY, "collections", self._upsert_collection),
            "pages": (PAGES_QUERY, "pages", self._upsert_page),
            "blogs": (BLOGS_QUERY, "blogs", self._upsert_blog),
            "redirects": (REDIRECTS_QUERY, "urlRedirects", self._upsert_redirect),
        }

        if resource not in query_map:
            return 0, 0

        query, root_field, upsert_fn = query_map[resource]
        processed = 0
        failed = 0
        cursor: str | None = None
        has_next = True

        while has_next:
            variables: dict[str, Any] = {
                "first": self.settings.sync_batch_size,
                "after": cursor,
            }
            try:
                data = await client.execute(query, variables)
            except ShopifyPermissionError as exc:
                if resource == "redirects":
                    logger.warning(
                        "Skipping Shopify redirects sync for store={} because the app token cannot access urlRedirects: {}",
                        store.shop_domain,
                        exc,
                    )
                    return processed, failed + 1
                raise
            connection = data.get(root_field, {})
            page_info = connection.get("pageInfo", {})
            edges = connection.get("edges", [])

            for edge in edges:
                try:
                    await upsert_fn(store, edge["node"])
                    processed += 1
                except Exception as exc:
                    failed += 1
                    logger.warning("Failed to upsert {} node: {}", resource, exc)

            has_next = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")

        return processed, failed

    async def _upsert_product(self, store: Store, node: dict[str, Any]) -> None:
        seo = node.get("seo") or {}
        await self.product_repo.upsert(
            store_id=store.id,
            shopify_id=node["id"],
            data={
                "title": node.get("title", ""),
                "handle": node.get("handle", ""),
                "description": node.get("descriptionHtml"),
                "status": node.get("status"),
                "vendor": node.get("vendor"),
                "product_type": node.get("productType"),
                "seo_title": seo.get("title"),
                "seo_description": seo.get("description"),
                "tags": node.get("tags"),
                "raw_data": node,
                "synced_at": datetime.now(UTC),
                "is_deleted": False,
            },
        )

    async def _upsert_collection(self, store: Store, node: dict[str, Any]) -> None:
        seo = node.get("seo") or {}
        count = (node.get("productsCount") or {}).get("count")
        await self.collection_repo.upsert(
            store_id=store.id,
            shopify_id=node["id"],
            data={
                "title": node.get("title", ""),
                "handle": node.get("handle", ""),
                "description": node.get("descriptionHtml"),
                "collection_type": "smart",
                "seo_title": seo.get("title"),
                "seo_description": seo.get("description"),
                "products_count": count,
                "raw_data": node,
                "synced_at": datetime.now(UTC),
                "is_deleted": False,
            },
        )

    async def _upsert_page(self, store: Store, node: dict[str, Any]) -> None:
        await self.page_repo.upsert(
            store_id=store.id,
            shopify_id=node["id"],
            data={
                "title": node.get("title", ""),
                "handle": node.get("handle", ""),
                "body_html": node.get("body"),
                "is_published": node.get("isPublished", True),
                "raw_data": node,
                "synced_at": datetime.now(UTC),
                "is_deleted": False,
            },
        )

    async def _upsert_blog(self, store: Store, node: dict[str, Any]) -> None:
        count = (node.get("articlesCount") or {}).get("count")
        await self.blog_repo.upsert(
            store_id=store.id,
            shopify_id=node["id"],
            data={
                "title": node.get("title", ""),
                "handle": node.get("handle", ""),
                "articles_count": count,
                "raw_data": node,
                "synced_at": datetime.now(UTC),
                "is_deleted": False,
            },
        )

    async def _upsert_redirect(self, store: Store, node: dict[str, Any]) -> None:
        await self.redirect_repo.upsert(
            store_id=store.id,
            shopify_id=node["id"],
            data={
                "path": node.get("path", ""),
                "target": node.get("target", ""),
                "raw_data": node,
                "synced_at": datetime.now(UTC),
                "is_deleted": False,
            },
        )

    async def mark_product_deleted(self, store: Store, shopify_id: str) -> None:
        await self.product_repo.mark_deleted(store.id, shopify_id)
