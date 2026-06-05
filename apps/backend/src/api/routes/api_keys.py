from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies import TenantContext, get_api_key_service, get_tenant_context
from src.models import APIKey
from src.schemas.api_key import APIKeyCreate, APIKeyCreated, APIKeyRead, APIKeyRotated
from src.services import APIKeyService

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: APIKeyCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    api_key_service: APIKeyService = Depends(get_api_key_service),
) -> APIKeyCreated:
    return await api_key_service.create(
        organization_id=tenant.organization_id,
        payload=payload,
    )


@router.get("", response_model=list[APIKeyRead])
async def list_api_keys(
    tenant: TenantContext = Depends(get_tenant_context),
    api_key_service: APIKeyService = Depends(get_api_key_service),
) -> list[APIKey]:
    return await api_key_service.list(organization_id=tenant.organization_id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    api_key_service: APIKeyService = Depends(get_api_key_service),
) -> Response:
    await api_key_service.delete(
        organization_id=tenant.organization_id,
        api_key_id=id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/rotate", response_model=APIKeyRotated)
async def rotate_api_key(
    id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    api_key_service: APIKeyService = Depends(get_api_key_service),
) -> APIKeyRotated:
    return await api_key_service.rotate(
        organization_id=tenant.organization_id,
        api_key_id=id,
    )
