"""Shopify OAuth 2.0 flow for Partner App installation."""

import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
from jose import JWTError, jwt
from loguru import logger

from app.config.settings import Settings, get_settings
from app.core.exceptions import IntegrationError, ShopifyAuthError


def normalize_shop_domain(shop: str) -> str:
    """Normalize a shop identifier to *.myshopify.com format."""
    shop = shop.strip().lower()
    shop = re.sub(r"^https?://", "", shop)
    shop = shop.rstrip("/")

    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"

    if not re.match(r"^[a-z0-9][a-z0-9-]*\.myshopify\.com$", shop):
        raise IntegrationError("Invalid shop domain format", error_code="INVALID_SHOP_DOMAIN")

    return shop


class ShopifyOAuthService:
    """Handles Shopify OAuth authorization and token exchange."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build_authorization_url(self, shop_domain: str, user_id: UUID) -> tuple[str, str]:
        """Return (authorization_url, state_token) for the OAuth redirect."""
        shop = normalize_shop_domain(shop_domain)
        state = self._create_state_token(user_id, shop)
        nonce = secrets.token_urlsafe(16)

        params = {
            "client_id": self.settings.shopify_api_key,
            "scope": self.settings.shopify_scopes,
            "redirect_uri": self.settings.shopify_redirect_uri,
            "state": state,
        }

        query = urlencode(params)
        auth_url = f"https://{shop}/admin/oauth/authorize?{query}"

        logger.info("Built Shopify OAuth URL for shop={} user={}", shop, user_id)
        return auth_url, state

    def verify_state_token(self, state: str) -> dict[str, Any]:
        """Validate and decode the OAuth state JWT."""
        try:
            payload = jwt.decode(
                state,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise ShopifyAuthError("Invalid or expired OAuth state", error_code="INVALID_OAUTH_STATE") from exc

        if payload.get("type") != "shopify_oauth":
            raise ShopifyAuthError("Invalid OAuth state type", error_code="INVALID_OAUTH_STATE")

        return payload

    async def exchange_code_for_token(self, shop_domain: str, code: str) -> dict[str, Any]:
        """Exchange authorization code for a permanent access token."""
        shop = normalize_shop_domain(shop_domain)
        url = f"https://{shop}/admin/oauth/access_token"

        payload = {
            "client_id": self.settings.shopify_api_key,
            "client_secret": self.settings.shopify_api_secret,
            "code": code,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code != 200:
            logger.error(
                "Shopify token exchange failed: status={} body={}",
                response.status_code,
                response.text,
            )
            raise ShopifyAuthError(
                "Failed to exchange authorization code",
                error_code="TOKEN_EXCHANGE_FAILED",
            )

        data = response.json()
        if "access_token" not in data:
            raise ShopifyAuthError("No access token in Shopify response", error_code="TOKEN_MISSING")

        logger.info("Successfully exchanged OAuth code for shop={}", shop)
        return {
            "access_token": data["access_token"],
            "scope": data.get("scope", self.settings.shopify_scopes),
        }

    def verify_hmac(self, query_params: dict[str, str]) -> bool:
        """Verify Shopify OAuth callback HMAC signature."""
        import hashlib
        import hmac

        received_hmac = query_params.get("hmac")
        if not received_hmac:
            return False

        sorted_params = "&".join(
            f"{k}={v}" for k, v in sorted(query_params.items()) if k not in ("hmac", "signature")
        )

        digest = hmac.new(
            self.settings.shopify_api_secret.encode(),
            sorted_params.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(digest, received_hmac)

    def _create_state_token(self, user_id: UUID, shop_domain: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.settings.shopify_oauth_state_expire_minutes)
        payload = {
            "sub": str(user_id),
            "shop": shop_domain,
            "type": "shopify_oauth",
            "exp": int(expire.timestamp()),
            "iat": int(datetime.now(UTC).timestamp()),
        }
        return jwt.encode(payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)
