#app/main.py
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.api.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME
)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

app.include_router(api_router)