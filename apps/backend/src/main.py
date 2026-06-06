from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from contextlib import asynccontextmanager
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.router import api_router
from src.api.routes.health import router as health_router
from src.core.config import settings
from src.core.logging import configure_logging
from src.middleware.correlation_id import CorrelationIdMiddleware
from src.ws.manager import manager

configure_logging(json_logs=settings.is_production)

logger = logging.getLogger(__name__)


async def _redis_subscriber() -> None:
    client = aioredis.from_url(
        settings.redis_url, decode_responses=True, protocol=2, health_check_interval=0
    )
    pubsub = client.pubsub()
    try:
        await pubsub.psubscribe("notifications:*")
    except Exception:
        logger.exception("Redis subscriber failed to connect; live notifications disabled.")
        await client.aclose()
        return
    logger.info("Redis notification subscriber started.")
    try:
        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue
            channel: str = message["channel"]
            try:
                org_id = UUID(channel.split(":")[-1])
                payload = json.loads(message["data"])
                await manager.broadcast_to_org(org_id, payload)
            except Exception:
                logger.exception("Error forwarding notification.", extra={"channel": channel})
    except asyncio.CancelledError:
        logger.info("Redis notification subscriber shutting down.")
    except Exception:
        logger.exception("Redis notification subscriber crashed.")
    finally:
        with contextlib.suppress(Exception):
            await pubsub.punsubscribe("notifications:*")
        with contextlib.suppress(Exception):
            await client.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    subscriber_task = asyncio.create_task(_redis_subscriber())
    try:
        yield
    finally:
        subscriber_task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await subscriber_task


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if settings.is_production:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.include_router(health_router)
    app.include_router(api_router)
    return app


app = create_app()
