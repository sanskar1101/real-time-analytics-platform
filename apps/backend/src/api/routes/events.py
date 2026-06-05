from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.api.dependencies import get_current_api_key, get_event_ingestion_service
from src.models import APIKey
from src.schemas.event import EventAccepted, EventBatchAccepted, EventBatchCreate, EventCreate
from src.services import EventIngestionService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventAccepted, status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(
    payload: EventCreate,
    api_key: APIKey = Depends(get_current_api_key),
    event_service: EventIngestionService = Depends(get_event_ingestion_service),
) -> EventAccepted:
    event = await event_service.ingest_single(api_key=api_key, payload=payload)
    return EventAccepted(id=event.id)


@router.post("/batch", response_model=EventBatchAccepted, status_code=status.HTTP_202_ACCEPTED)
async def ingest_event_batch(
    payload: EventBatchCreate,
    api_key: APIKey = Depends(get_current_api_key),
    event_service: EventIngestionService = Depends(get_event_ingestion_service),
) -> EventBatchAccepted:
    return await event_service.ingest_batch(api_key=api_key, payload=payload)


@router.post("/upload-csv", response_model=EventBatchAccepted, status_code=status.HTTP_202_ACCEPTED)
async def upload_events_csv(
    file: UploadFile = File(...),
    api_key: APIKey = Depends(get_current_api_key),
    event_service: EventIngestionService = Depends(get_event_ingestion_service),
) -> EventBatchAccepted:
    return await event_service.ingest_csv(api_key=api_key, upload=file)
