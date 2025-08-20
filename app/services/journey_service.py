import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List, Tuple

from app.api.core.config import settings
from app.schemas.schemas import FlightEvent, JourneyReturn, JourneyItem

class JourneyService:
    def __init__(self) -> None:
        self._flight_events: List[FlightEvent] | None = None

    def _load_events(self) -> List[FlightEvent]:
        path: Path = Path(settings.FLIGHT_EVENTS_PATH)
        if self._flight_events is None:
            with path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            self._flight_events = [FlightEvent(**item) for item in raw]
        return self._flight_events

    @staticmethod
    def _to_item(e: FlightEvent) -> JourneyItem:
        return JourneyItem(
            flight_number=e.flight_number,
            from_=e.departure_city,
            to=e.arrival_city,
            departure_time=e.departure_datetime.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            arrival_time=e.arrival_datetime.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )

    def find_journeys(self, day_utc: date, origin: str, destination: str) -> List[JourneyReturn]:
        events = self._load_events()

        day_events: List[FlightEvent] = [
            e for e in events if e.departure_datetime.astimezone(timezone.utc).date() == day_utc
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

        # Orden: menos conexiones, luego hora de salida
        result.sort(key=lambda j: (j.connections, j.path[0].departure_time))
        return result


def get_journey_service():
    return JourneyService()