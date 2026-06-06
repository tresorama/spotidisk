from pydantic_settings import BaseSettings

class ConfigStatic(BaseSettings):
    # Spotify
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    # Server
    debug: bool = True
    log_level: str = "info"
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


config_static = ConfigStatic()
