"""
config.py
---------
Application-level configuration management using Pydantic Settings.
This ensures strict type validation for environment variables, failing fast
if critical keys (like OPENAI_API_KEY) are missing.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Global application settings.
    Attributes are automatically read from environment variables.
    """
    # Project Info
    PROJECT_NAME: str = "FlowGuard-Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development" # 'development' or 'production'

    # Security (CORS)
    # In production, this should be a specific list of origins
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # External APIs
    OPENAI_API_KEY: str
    
    # Vector Database (Qdrant)
    QDRANT_HOST: str = "qdrant" # Service name in Docker Compose
    QDRANT_PORT: int = 6333
    
    # Model Configuration
    # We use GPT-4o-mini as specified for cost-effective, high-frequency telemetry parsing
    MODEL_NAME: str = "gpt-4o-mini"

    # Configuration class for Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of Settings to avoid reading the file repeatedly.
    """
    return Settings()