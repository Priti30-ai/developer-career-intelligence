import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings and configuration."""
    app_name: str = os.getenv("APP_NAME", "Developer Career Intelligence System")
    version: str = os.getenv("VERSION", "0.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: tuple = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )


settings = Settings()
