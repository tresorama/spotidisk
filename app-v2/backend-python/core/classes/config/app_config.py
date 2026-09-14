from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.classes.logger.logger import Logger
from core.classes.utils.utils_os import UtilsOS

class EnvironmentVariables(BaseSettings):
  """Environment Variables, read from .env file or environment variables"""
  model_config = SettingsConfigDict(
    env_file=".env",
    case_sensitive=True,
  )
  BACKEND_PORT: int
  FRONTEND_PORT: int
  STATIC_DIR_TO_SERVE_PATH: str | None = None
  LOG_LEVEL: Literal["debug", "info"]
  APP_MODE: Literal["regular", "test-e2e"]
    
class AppConfigRuntime():
  """App Config part of runtime stuff"""
  def __init__(self, envVars: EnvironmentVariables):
    self.binaries_path: Path = Path.cwd() / ".bin"
    self.user_config_file_name: str = "config.json"
    if (envVars.APP_MODE == "test-e2e"):
      self.user_config_file_name = "config_test_e2e.json"
    self.user_config_dir_path: Path = Path(UtilsOS.getUserAppDataDirectoryPath()) / "Spotidisk"
    self.user_config_file_path: Path = self.user_config_dir_path / self.user_config_file_name
    self.cors_origins: list[str] = [
      f"http://localhost:{envVars.FRONTEND_PORT}",
    ]
  def dump(self):
    return {
      "binaries_path": str(self.binaries_path),
      "user_config_file_name": self.user_config_file_name,
      "user_config_dir_path": str(self.user_config_dir_path),
      "user_config_file_path": str(self.user_config_file_path),
      "cors_origins": self.cors_origins
    }

class AppConfig():
  """App Config"""
  def __init__(
    self,
    logger: Logger,
    envVars: EnvironmentVariables,
    runtime: AppConfigRuntime,
  ):
    self.logger: Logger = logger
    self.envVars: EnvironmentVariables = envVars
    self.runtime: AppConfigRuntime = runtime