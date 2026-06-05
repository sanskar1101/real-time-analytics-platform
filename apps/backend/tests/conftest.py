from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

# Use test DB/Redis from environment or fall back to CI service defaults.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture
async def client():
    # Import after env vars are set so settings picks them up.
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
