from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os


class AppConfig(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Household Dashboard")
    database_path: Path = Path(os.getenv("DATABASE_PATH", "./data/dashboard.sqlite3"))
    photo_dir: Path = Path(os.getenv("PHOTO_DIR", "./photos"))
    photo_max_images: int = int(os.getenv("PHOTO_MAX_IMAGES", "500"))
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-this-password")
    session_secret: str = os.getenv("SESSION_SECRET", "dev-session-secret")
    display_public: bool = os.getenv("DISPLAY_PUBLIC", "true").lower() == "true"
    calendar_refresh_seconds: int = int(os.getenv("CALENDAR_REFRESH_SECONDS", "900"))
    weather_refresh_seconds: int = int(os.getenv("WEATHER_REFRESH_SECONDS", "900"))
    frigate_timeout_seconds: float = float(os.getenv("FRIGATE_TIMEOUT_SECONDS", "8"))


@lru_cache
def get_config() -> AppConfig:
    config = AppConfig()
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    config.photo_dir.mkdir(parents=True, exist_ok=True)
    return config
