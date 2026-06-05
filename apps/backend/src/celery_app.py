from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from src.core.config import settings

celery_app = Celery(
    "real_time_analysis",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.tasks.events", "src.tasks.alerts", "src.tasks.reports"],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    timezone="UTC",
    beat_schedule={
        "evaluate-alerts-every-minute": {
            "task": "evaluate_alerts",
            "schedule": 60.0,
        },
        "dispatch-daily-reports": {
            "task": "dispatch_scheduled_reports",
            "schedule": crontab(hour=0, minute=0),
            "args": ("DAILY",),
        },
        "dispatch-weekly-reports": {
            "task": "dispatch_scheduled_reports",
            "schedule": crontab(hour=0, minute=0, day_of_week=1),
            "args": ("WEEKLY",),
        },
        "dispatch-monthly-reports": {
            "task": "dispatch_scheduled_reports",
            "schedule": crontab(hour=0, minute=0, day_of_month=1),
            "args": ("MONTHLY",),
        },
    },
)
