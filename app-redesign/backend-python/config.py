from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Spotify
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    # Paths
    download_path: Path = Path("~/Music/Sunnify").expanduser()
    config_file: Path = Path("~/.config/sunnify/config.json").expanduser()

    # Server
    debug: bool = True
    log_level: str = "info"
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
