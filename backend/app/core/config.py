import os
from dataclasses import dataclass
from typing import Optional


def _load_env_file() -> None:
    """Load key-value pairs from .env if present and not already set in environment."""
    for env_path in (".env", "../.env"):
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass


_load_env_file()


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
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN", "").strip() or None


settings = Settings()

