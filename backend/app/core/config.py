from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Wicked App API"
    VERSION: str = "0.1.0"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB_NAME: str = "wicked_db"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://wickednas:5173"]
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        case_sensitive=True
    )


settings = Settings()
