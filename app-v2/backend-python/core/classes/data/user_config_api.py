from __future__ import annotations
import json
from pathlib import Path

from models.user_config import UserConfig

from core.classes.logger.logger import Logger
from core.classes.utils.utils_os import UtilsOS

class UserConfigApi:
    def __init__(
      self, 
      logger: Logger,
      config_file: Path,
    ):
      self.logger: Logger = logger
      self.config_file: Path = Path(config_file).expanduser()
      self.config_as_object_default: UserConfig = UserConfig(**{
        "version": 1,
        "setting_disk_download_path": str(Path(UtilsOS.getUserHomeDirectoryPath()) / "Desktop" / "Spotidisk"),
        "setting_disk_filename_pattern": "{index} {title} - {artist}",
        "setting_disk_format": "mp3",
        "setting_disk_quality": "192",
        "setting_disk_add_meta_tags": True,
        "data_playlists": [],
        "data_playlists_songs": {},
      })
      self.config_as_object: UserConfig = self.config_as_object_default
    
    def idrate_from_disk(self):
      """
      Load config file from disk and set config object in instance. 
      If file does not exist, a new one is created with defaults
      """
      self.logger.info(f"UserConfigApi - Idrating UserConfig from disk at path: {self.config_file}")
      
      # check if config fil exists
      file_exists = self.config_file.exists()
      
      # if not, create it with defaults
      if not file_exists:
        self.logger.warning(f"UserConfigApi - Config file not found on disk. Creating a new one with defaults...")
        createdResult = self.write_config(self.config_as_object_default)
        if not createdResult[0]:
          self.logger.error(f"UserConfigApi - Error creating config file: {createdResult[1]}")
          raise Exception(f"Error creating config file: {createdResult[1]}")
        self.logger.info(f"UserConfigApi - Config file created!")
        
      # read config file and set config object in instance
      self.logger.info(f"UserConfigApi - Reading config file...")
      self.read_config()
    
    def read_config(self):
      """Read config file from disk, parse it, and set config object in instance"""
      # get raw json (or fail)
      # rawJson = None
      try:
        with open(self.config_file, "r", encoding="utf-8") as f:
          rawJson = json.load(f)
      except (json.JSONDecodeError, IOError) as e:
        self.logger.error(f"UserConfigApi - Error loading config file: {e}")
        raise e
      self.logger.info(f"UserConfigApi - Loaded config file as json.")
      
      # parse json to object (or fail)
      # parsedConfig: None | UserConfig = None
      try: 
        parsedConfig = UserConfig(**rawJson)
      except Exception as e:
        self.logger.error(f"UserConfigApi - Error parsing config file: {e}")
        raise e
      self.logger.info(f"UserConfigApi - Loaded config file as object (parsed with pydantic).")
      
      # set config object in instance
      self.config_as_object = parsedConfig

    def write_config(self, config_as_object: UserConfig):
        """Write config to file"""
        # ensure parent dir exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        # convert to json
        try:
          data = config_as_object.model_dump()
          # self.logger.info(f"json: {data}")
        except Exception as e:
          self.logger.error(f"UserConfigApi - Error converting config to json: {e}")
          return (False, "CONVERT_TO_JSON_ERROR")
        # write to file
        try:
          Path(self.config_file).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
          )
        except Exception as e:
          self.logger.error(f"UserConfigApi - Error writing config to file: {e}")
          return (False, "WRITE_TO_FILE_ERROR")
        # success
        return (True, "OK")
    
    def get_deep_clone_of_config(self) -> UserConfig:
      """Return a deep clone of the config object"""
      return self.config_as_object.model_copy()
      
    def write_config_to_disk_and_reidrate(self, new_config_as_object: UserConfig) -> None:
      """Write a nw verion of config to disk and refresh instance"""
      writeResult = self.write_config(new_config_as_object)
      if (writeResult[0]):
        # re-set instance prop (avoiding IO disk)
        self.config_as_object = new_config_as_object
    
    