from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import redis as sync_redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.celery_app import celery_app
from src.core.config import settings
from src.db.session import AsyncSessionLocal
from src.models.alert import Alert
from src.models.alert_metric_type import AlertMetricType
from src.models.alert_status import AlertStatus
from src.models.event import Event
from src.repositories.alert import AlertRepository
from src.repositories.notification import NotificationRepository

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="evaluate_alerts",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_alerts(self) -> None:
    logger.info("Starting alert evaluation cycle.", extra={"task_id": self.request.id})
    asyncio.run(_evaluate_alerts())
    logger.info("Alert evaluation cycle complete.", extra={"task_id": self.request.id})


async def _evaluate_alerts() -> None:
    async with AsyncSessionLocal() as session:
        alert_repo = AlertRepository(session)
        notification_repo = NotificationRepository(session)

        alerts = await alert_repo.list_evaluatable()
        logger.info("Evaluating alerts.", extra={"count": len(alerts)})

        for alert in alerts:
            try:
                await _evaluate_single_alert(session, alert, alert_repo, notification_repo)
            except Exception:
                logger.exception("Failed to evaluate alert.", extra={"alert_id": str(alert.id)})


async def _evaluate_single_alert(
    session: AsyncSession,
    alert: Alert,
    alert_repo: AlertRepository,
    notification_repo: NotificationRepository,
) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=alert.window_minutes)

    metric_value = await _compute_metric(session, alert, window_start, now)
    was_triggered = alert.status == AlertStatus.TRIGGERED

    if metric_value >= alert.threshold:
        if not was_triggered:
            alert.status = AlertStatus.TRIGGERED
            await session.flush()

            await alert_repo.create_history(
                alert_id=alert.id,
                metric_value=metric_value,
                status=AlertStatus.TRIGGERED,
            )

            notification = await notification_repo.create(
                organization_id=alert.organization_id,
                title=f"Alert triggered: {alert.name}",
                message=(
                    f"{alert.metric_type.value} reached {metric_value:.0f} "
                    f"in the last {alert.window_minutes}m "
                    f"(threshold: {alert.threshold:.0f})"
                ),
            )
            await session.commit()

            _publish_notification(
                organization_id=alert.organization_id,
                notification_id=notification.id,
                title=notification.title,
                message=notification.message,
                created_at=notification.created_at.isoformat(),
            )
            logger.info(
                "Alert triggered.",
                extra={"alert_id": str(alert.id), "metric_value": metric_value},
            )
    else:
        if was_triggered:
            alert.status = AlertStatus.RESOLVED
            await session.flush()

            await alert_repo.create_history(
                alert_id=alert.id,
                metric_value=metric_value,
                status=AlertStatus.RESOLVED,
            )
            await session.commit()
            logger.info(
                "Alert resolved.",
                extra={"alert_id": str(alert.id), "metric_value": metric_value},
            )


async def _compute_metric(
    session: AsyncSession,
    alert: Alert,
    window_start: datetime,
    window_end: datetime,
) -> float:
    if alert.metric_type == AlertMetricType.EVENT_COUNT:
        stmt = (
            select(func.count())
            .select_from(Event)
            .where(
                Event.organization_id == alert.organization_id,
                Event.event_timestamp >= window_start,
                Event.event_timestamp <= window_end,
            )
        )
    else:
        # ERROR_COUNT: events whose name contains "error" (case-insensitive)
        stmt = (
            select(func.count())
            .select_from(Event)
            .where(
                Event.organization_id == alert.organization_id,
                Event.event_timestamp >= window_start,
                Event.event_timestamp <= window_end,
                Event.event_name.ilike("%error%"),
            )
        )

    result = await session.execute(stmt)
    return float(result.scalar_one())


def _publish_notification(
    *,
    organization_id: UUID,
    notification_id: UUID,
    title: str,
    message: str,
    created_at: str,
) -> None:
    """Publish a notification to the Redis pub/sub channel for the given org."""
    try:
        client = sync_redis.from_url(settings.redis_url, decode_responses=True)
        channel = f"notifications:{organization_id}"
        payload = json.dumps(
            {
                "type": "notification",
                "id": str(notification_id),
                "title": title,
                "message": message,
                "created_at": created_at,
            }
        )
        client.publish(channel, payload)
        client.close()
    except Exception:
        logger.exception(
            "Failed to publish notification to Redis.",
            extra={"organization_id": str(organization_id)},
        )
