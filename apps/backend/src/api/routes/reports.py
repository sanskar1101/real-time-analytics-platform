from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import TenantContext, get_report_service, get_tenant_context
from src.schemas.report import PaginatedReports, ReportCreate, ReportRead
from src.services.report import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: ReportService = Depends(get_report_service),
) -> ReportRead:
    report = await service.create(organization_id=ctx.organization_id, payload=payload)
    return ReportRead.model_validate(report)


@router.get("", response_model=PaginatedReports)
async def list_reports(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: TenantContext = Depends(get_tenant_context),
    service: ReportService = Depends(get_report_service),
) -> PaginatedReports:
    return await service.list(
        organization_id=ctx.organization_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{report_id}", response_model=ReportRead)
async def get_report(
    report_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: ReportService = Depends(get_report_service),
) -> ReportRead:
    report = await service.get(
        report_id=report_id,
        organization_id=ctx.organization_id,
    )
    return ReportRead.model_validate(report)
