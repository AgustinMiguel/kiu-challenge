from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
from typing import List


class FlightEvent(BaseModel):
    flight_number: str
    departure_city: str
    arrival_city: str
    departure_datetime: datetime
    arrival_datetime: datetime


    @field_validator("departure_city", "arrival_city")
    @classmethod
    def normalize_city(cls, v: str) -> str:
        return v.strip().upper()


    @field_validator("departure_datetime", "arrival_datetime")
    @classmethod
    def ensure_utc(cls, dt: datetime) -> datetime:
        # Fuerza timezone-aware en UTC
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)


class JourneyItem(BaseModel):
    flight_number: str
    from_: str
    to: str
    departure_time: str
    arrival_time: str


class JourneyReturn(BaseModel):
    connections: int
    path: List[JourneyItem]