"""
FastAPI Configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WeeFarm Predictive Maintenance API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:0000@localhost:5432/weefarm_db"
    )
    
    # Security
    API_KEY: str = os.getenv("API_KEY", "weefarm-secret-key-change-in-production")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:8501",  # Streamlit
        "http://localhost:3000",  # React (if needed)
        "http://localhost:8000",  # FastAPI docs
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
