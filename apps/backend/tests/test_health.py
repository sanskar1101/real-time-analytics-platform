from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_expected_shape(client: AsyncClient) -> None:
    """Health endpoint always returns all required keys regardless of service state."""
    response = await client.get("/health")

    assert response.status_code in (200, 503)
    body = response.json()
    assert "status" in body
    assert "database" in body
    assert "redis" in body
    assert body["status"] in ("healthy", "unhealthy")


@pytest.mark.asyncio
async def test_health_correlation_id_propagated(client: AsyncClient) -> None:
    """X-Correlation-ID sent in the request is echoed back in the response."""
    correlation_id = "test-correlation-id-1234"
    response = await client.get("/health", headers={"X-Correlation-ID": correlation_id})

    assert response.headers.get("x-correlation-id") == correlation_id


@pytest.mark.asyncio
async def test_health_generates_correlation_id_when_absent(client: AsyncClient) -> None:
    """Response always includes X-Correlation-ID even when not provided by caller."""
    response = await client.get("/health")

    assert "x-correlation-id" in response.headers
    assert len(response.headers["x-correlation-id"]) > 0


@pytest.mark.asyncio
async def test_api_docs_accessible(client: AsyncClient) -> None:
    """OpenAPI JSON schema is served at /api/openapi.json."""
    response = await client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
