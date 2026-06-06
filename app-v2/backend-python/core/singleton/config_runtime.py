from pathlib import Path
from pydantic_settings import BaseSettings

from core.singleton.config_user_file import config_user_file

class ConfigRuntime(BaseSettings):
    # Paths
    download_path: Path = Path("~/Music/Sunnify").expanduser()
    config_file: Path = config_user_file.get_file_path()
    
config_runtime = ConfigRuntime()
