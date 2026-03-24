import json

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Wicked App API"
    VERSION: str = "0.1.0"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB_NAME: str = "wicked_db"
    
    # CORS settings (accepts JSON array or comma-separated string)
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8080"]
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            # Intentar JSON primero
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            # Fallback CSV
            return [origin.strip() for origin in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()
