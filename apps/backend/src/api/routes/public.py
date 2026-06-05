from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.repositories.dashboard import DashboardRepository
from src.schemas.widget import WidgetRead

router = APIRouter(prefix="/public", tags=["Public"])


class PublicDashboardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    widgets: list[WidgetRead]


@router.get("/dashboard/{dashboard_id}", response_model=PublicDashboardRead)
async def get_public_dashboard(
    dashboard_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> PublicDashboardRead:
    repo = DashboardRepository(session)
    dashboard = await repo.get_public_with_widgets(dashboard_id)
    if dashboard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found.",
        )
    return PublicDashboardRead.model_validate(dashboard)
