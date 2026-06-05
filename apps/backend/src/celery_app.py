from __future__ import annotations

from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "real_time_analysis",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.tasks.events"],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    timezone="UTC",
)
