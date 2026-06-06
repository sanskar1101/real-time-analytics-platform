from fastapi import APIRouter

from src.api.routes import (
    alerts,
    analytics,
    api_keys,
    auth,
    dashboards,
    events,
    notifications,
    public,
    reports,
    widgets,
    ws,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)
api_router.include_router(api_keys.router)
api_router.include_router(auth.router)
api_router.include_router(dashboards.router)
api_router.include_router(events.router)
api_router.include_router(notifications.router)
api_router.include_router(public.router)
api_router.include_router(reports.router)
api_router.include_router(widgets.router)
api_router.include_router(ws.router)
