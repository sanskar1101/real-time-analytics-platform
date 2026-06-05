from __future__ import annotations

import asyncio
import csv
import json
from io import StringIO
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import APIKey, Event
from src.repositories import EventRepository
from src.schemas.event import EventBatchAccepted, EventBatchCreate, EventCreate


class EventIngestionService:
    def __init__(self, *, session: AsyncSession, event_repository: EventRepository) -> None:
        self._session = session
        self._events = event_repository

    async def ingest_single(self, *, api_key: APIKey, payload: EventCreate) -> Event:
        event = await self._events.create(
            organization_id=api_key.organization_id,
            source=api_key.name,
            event_name=payload.event_name,
            event_timestamp=payload.event_timestamp,
            payload=payload.payload,
        )
        await self._session.commit()
        return event

    async def ingest_batch(
        self,
        *,
        api_key: APIKey,
        payload: EventBatchCreate,
    ) -> EventBatchAccepted:
        created_events = await self._events.create_many(
            organization_id=api_key.organization_id,
            source=api_key.name,
            events=[
                (event.event_name, event.event_timestamp, event.payload)
                for event in payload.events
            ],
        )
        await self._session.commit()
        return EventBatchAccepted(
            accepted_count=len(created_events),
            event_ids=[event.id for event in created_events],
        )

    async def ingest_csv(self, *, api_key: APIKey, upload: UploadFile) -> EventBatchAccepted:
        content = await upload.read()
        parsed_events = await asyncio.to_thread(self._parse_csv, content)
        return await self.ingest_batch(
            api_key=api_key,
            payload=EventBatchCreate(events=parsed_events),
        )

    @staticmethod
    def _parse_csv(content: bytes) -> list[EventCreate]:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file must be UTF-8 encoded.",
            ) from exc

        reader = csv.DictReader(StringIO(text))
        expected_fields = {"event_name", "event_timestamp", "payload"}
        if reader.fieldnames is None or not expected_fields.issubset(set(reader.fieldnames)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must include event_name, event_timestamp, and payload columns.",
            )

        events: list[EventCreate] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                payload = json.loads(row.get("payload") or "{}")
                events.append(
                    EventCreate(
                        event_name=row.get("event_name") or "",
                        event_timestamp=row.get("event_timestamp") or "",
                        payload=payload,
                    )
                )
            except (json.JSONDecodeError, ValidationError, TypeError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid CSV event at row {row_number}.",
                ) from exc

        if not events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file did not contain any events.",
            )
        return events


class EventProcessingService:
    def __init__(self, *, session: AsyncSession, event_repository: EventRepository) -> None:
        self._session = session
        self._events = event_repository

    async def mark_processed(self, event_id: UUID) -> bool:
        event = await self._events.get_by_id(event_id)
        if event is None:
            return False

        event.processed = True
        await self._session.commit()
        return True
