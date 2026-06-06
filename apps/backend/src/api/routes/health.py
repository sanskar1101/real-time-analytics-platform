from __future__ import annotations

import logging

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.core.config import settings
from src.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", include_in_schema=True)
async def health_check() -> JSONResponse:
    result: dict[str, str] = {"status": "healthy", "database": "ok", "redis": "ok"}
    healthy = True

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Health check: database unreachable.")
        result["database"] = "error"
        healthy = False

    try:
        client = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        await client.ping()
        await client.aclose()
    except Exception:
        logger.exception("Health check: redis unreachable.")
        result["redis"] = "error"
        healthy = False

    if not healthy:
        result["status"] = "unhealthy"

    return JSONResponse(
        content=result,
        status_code=200 if healthy else 503,
    )
