"""Tests for Shopify integration utilities."""

import base64
import hashlib
import hmac

import pytest

from app.integrations.shopify.oauth import ShopifyOAuthService, normalize_shop_domain


def test_normalize_shop_domain_adds_suffix():
    assert normalize_shop_domain("my-store") == "my-store.myshopify.com"


def test_normalize_shop_domain_strips_protocol():
    assert normalize_shop_domain("https://my-store.myshopify.com") == "my-store.myshopify.com"


def test_normalize_shop_domain_invalid():
    with pytest.raises(Exception):
        normalize_shop_domain("not valid!!")


def test_oauth_hmac_verification(test_settings):
    oauth = ShopifyOAuthService(test_settings)
    params = {
        "code": "test_code",
        "shop": "my-store.myshopify.com",
        "state": "test_state",
        "timestamp": "1234567890",
    }
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    digest = hmac.new(
        test_settings.shopify_api_secret.encode(),
        sorted_params.encode(),
        hashlib.sha256,
    ).hexdigest()
    params["hmac"] = digest
    assert oauth.verify_hmac(params) is True


def test_webhook_hmac_verification(test_settings):
    from app.integrations.shopify.webhooks import ShopifyWebhookHandler

    handler = ShopifyWebhookHandler.__new__(ShopifyWebhookHandler)
    handler.settings = test_settings

    body = b'{"id": 123, "title": "Test Product"}'
    digest = hmac.new(
        test_settings.shopify_api_secret.encode(),
        body,
        hashlib.sha256,
    ).digest()
    header = base64.b64encode(digest).decode()

    assert handler.verify_signature(body, header) is True
    assert handler.verify_signature(body, "invalid") is False
