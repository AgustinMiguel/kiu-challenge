#app/api/core/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KIU - Challenge"
    FLIGHT_EVENTS_PATH: str
    
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
