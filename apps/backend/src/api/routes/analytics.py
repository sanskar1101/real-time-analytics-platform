from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import TenantContext, get_analytics_service, get_tenant_context
from src.schemas.analytics import EventCountResponse, EventsByDayResponse, EventsByTypeResponse
from src.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/event-count", response_model=EventCountResponse)
async def get_event_count(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    ctx: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> EventCountResponse:
    return await service.get_event_count(
        organization_id=ctx.organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/events-by-day", response_model=EventsByDayResponse)
async def get_events_by_day(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    ctx: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> EventsByDayResponse:
    return await service.get_events_by_day(
        organization_id=ctx.organization_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/events-by-type", response_model=EventsByTypeResponse)
async def get_events_by_type(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    ctx: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> EventsByTypeResponse:
    return await service.get_events_by_type(
        organization_id=ctx.organization_id,
        start_date=start_date,
        end_date=end_date,
    )
