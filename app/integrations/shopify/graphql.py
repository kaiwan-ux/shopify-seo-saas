"""Async Shopify Admin GraphQL API client."""

from typing import Any

import httpx
from loguru import logger

from app.config.settings import Settings, get_settings
from app.core.exceptions import IntegrationError, ShopifyAuthError, ShopifyPermissionError
from app.utils.retry import with_retry


class ShopifyGraphQLClient:
    """Production async client for the Shopify Admin GraphQL API."""

    def __init__(
        self,
        shop_domain: str,
        access_token: str,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.endpoint = (
            f"https://{shop_domain}/admin/api/{self.settings.shopify_api_version}/graphql.json"
        )

    async def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation with retry on transient failures."""
        return await with_retry(
            lambda: self._execute_once(query, variables),
            max_attempts=3,
            operation_name=f"shopify_graphql:{self.shop_domain}",
            retry_on=(httpx.TransportError, httpx.TimeoutException, IntegrationError),
        )

    async def _execute_once(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
        payload = {"query": query, "variables": variables or {}}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)

        if response.status_code == 401:
            raise ShopifyAuthError(
                "Shopify access token is invalid or expired",
                error_code="SHOPIFY_TOKEN_EXPIRED",
            )

        if response.status_code == 429:
            raise IntegrationError(
                "Shopify rate limit exceeded",
                error_code="SHOPIFY_RATE_LIMIT",
            )

        if response.status_code >= 400:
            logger.error(
                "Shopify GraphQL HTTP error: status={} body={}",
                response.status_code,
                response.text[:500],
            )
            raise IntegrationError(
                f"Shopify API error (HTTP {response.status_code})",
                error_code="SHOPIFY_API_ERROR",
            )

        data = response.json()

        if "errors" in data:
            error_messages = [e.get("message", str(e)) for e in data["errors"]]
            logger.error("Shopify GraphQL errors: {}", error_messages)
            if _is_access_denied_error(data["errors"]):
                raise ShopifyPermissionError(
                    f"Shopify GraphQL permission denied: {'; '.join(error_messages)}"
                )
            raise IntegrationError(
                f"Shopify GraphQL errors: {'; '.join(error_messages)}",
                error_code="SHOPIFY_GRAPHQL_ERROR",
            )

        return data.get("data", {})

    async def get_shop_info(self) -> dict[str, Any]:
        """Fetch basic shop metadata."""
        query = """
        query GetShop {
          shop {
            id
            name
            myshopifyDomain
            primaryDomain { url host }
            email
            currencyCode
          }
        }
        """
        data = await self.execute(query)
        return data.get("shop", {})


def _is_access_denied_error(errors: list[dict[str, Any]]) -> bool:
    return any("access denied" in str(error.get("message", error)).lower() for error in errors)
