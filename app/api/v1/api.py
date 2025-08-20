from fastapi import APIRouter

from app.api.v1.endpoints import journey


api_router = APIRouter()
api_router.include_router(journey.router, tags=["journeys"])