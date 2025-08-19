import json
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from app.api.core.config import settings
from app.schemas.schemas import FlightEvent, JourneyReturn, JourneyItem


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")


def _same_date_utc(dt: datetime, target: date) -> bool:
    return dt.astimezone(timezone.utc).date() == target


class JourneyService:
    def __init__(self, events_path: Path) -> None:
        self._events_path: Path = Path(events_path)
        self._flight_events: List[FlightEvent] | None = None

    def _load_events(self) -> List[FlightEvent]:
        if self._flight_events is None:
            with self._events_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            self._flight_events = [FlightEvent(**item) for item in raw]
        return self._flight_events

    @staticmethod
    def _to_item(e: FlightEvent) -> JourneyItem:
        return JourneyItem(
            flight_number=e.flight_number,
            from_=e.departure_city,
            to=e.arrival_city,
            departure_time=_fmt(e.departure_datetime),
            arrival_time=_fmt(e.arrival_datetime),
        )

    def find_journeys(self, day_utc: date, origin: str, destination: str) -> List[JourneyReturn]:
        origin = origin.strip().upper()
        destination = destination.strip().upper()

        events = self._load_events()

        day_events: List[FlightEvent] = [
            e for e in events if _same_date_utc(e.departure_datetime, day_utc)
        ]

        # Vuelos Directos
        direct_paths: List[Tuple[FlightEvent, ...]] = [
            (e,) for e in day_events
            if e.departure_city == origin and e.arrival_city == destination
            and (e.arrival_datetime - e.departure_datetime) <= timedelta(hours=24)
        ]

        # Vuelos con una conexión
        one_stop_paths: List[Tuple[FlightEvent, FlightEvent]] = []

        first_legs = [e for e in day_events if e.departure_city == origin]
        second_legs = [e for e in events if e.arrival_city == destination]

        for a in first_legs:
            for b in second_legs:
                if a.arrival_city != b.departure_city:
                    continue
                if b.departure_datetime < a.arrival_datetime:
                    continue
                layover = b.departure_datetime - a.arrival_datetime
                if layover > timedelta(hours=4):
                    continue
                total = b.arrival_datetime - a.departure_datetime
                if total > timedelta(hours=24):
                    continue
                one_stop_paths.append((a, b))

        seen = set()
        result: List[JourneyReturn] = []

        def add_path(path: Tuple[FlightEvent, ...]):
            key = tuple((e.flight_number, e.departure_datetime) for e in path)
            if key in seen:
                return
            seen.add(key)
            items = [self._to_item(e) for e in path]
            result.append(JourneyReturn(connections=len(path) - 1, path=items))

        for p in direct_paths:
            add_path(p)
        for p in one_stop_paths:
            add_path(p)

        return result


def get_journey_service():
    return JourneyService(settings.FLIGHT_EVENTS_PATH)