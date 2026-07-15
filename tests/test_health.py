import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "timestamp" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_version_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Shopify SEO SaaS"
    assert data["version"] == "0.1.0"
    assert "environment" in data
