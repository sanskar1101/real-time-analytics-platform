from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from src.celery_app import celery_app
from src.db.session import AsyncSessionLocal
from src.repositories import EventRepository
from src.services.event import EventProcessingService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
    name="process_event",
)
def process_event(self, event_id: str) -> bool:
    logger.info("Processing event.", extra={"event_id": event_id, "task_id": self.request.id})
    return asyncio.run(_process_event(UUID(event_id)))


async def _process_event(event_id: UUID) -> bool:
    async with AsyncSessionLocal() as session:
        service = EventProcessingService(
            session=session,
            event_repository=EventRepository(session),
        )
        processed = await service.mark_processed(event_id)
        logger.info(
            "Event processing completed.", extra={"event_id": str(event_id), "processed": processed}
        )
        return processed
