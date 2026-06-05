from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class EventCountResponse(BaseModel):
    total: int


class EventsByDayItem(BaseModel):
    date: date
    count: int


class EventsByDayResponse(BaseModel):
    items: list[EventsByDayItem]


class EventsByTypeItem(BaseModel):
    event_name: str
    count: int


class EventsByTypeResponse(BaseModel):
    items: list[EventsByTypeItem]
