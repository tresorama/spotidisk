import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings

from core.singleton.logger import logger

# constants
USER_CONFIG_FILE_NAME = "config--for-react-app.json"

class UserConfig(BaseSettings):
  def get_dir_path(self) -> Path:
    """Return the per-user config directory, creating it if needed."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))

    config_dir = Path(base) / "Sunnify"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
  
  def get_file_path(self) -> Path:
    """Return the path to config.json"""
    final_path = self.get_dir_path() / USER_CONFIG_FILE_NAME
    logger.info(f"Config file path: {final_path}")
    return final_path

config_user_file = UserConfig()