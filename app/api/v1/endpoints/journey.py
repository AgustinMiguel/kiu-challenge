from __future__ import annotations
from datetime import date
from typing import List
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse

from app.services.journey_service import JourneyService, get_journey_service
from app.schemas.schemas import JourneyReturn

router = APIRouter()

@router.get("/journeys/search", response_model=List[JourneyReturn])
async def journeys_search(
    date_: date = Query(..., alias="date", description="YYYY-MM-DD (UTC)"),
    from_: str = Query(..., alias="from", min_length=3, max_length=3, description="Origen (3 letras)"),
    to_: str = Query(..., alias="to", min_length=3, max_length=3, description="Destino (3 letras)"),
    journey_service: JourneyService = Depends(get_journey_service)
):
    journeys = journey_service.find_journeys(date_, from_, to_)
    return journeys
