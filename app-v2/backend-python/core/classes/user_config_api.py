from __future__ import annotations

import json
from pathlib import Path
from core.singleton.logger import logger
from models.new import UserConfig

userConfigDefaults = UserConfig(**{
  "version": 1,
  "download_path": "/Volumes/64GB/TRAKTOR/Sunnify",
  "filename_pattern": "{title} - {artist}",
  "format": "mp3",
  "quality": "192",
  "saved_playlists": [],
  "add_meta_tags": True,
  "show_preview": True,
  "playlists_songs_data": {},
})
logger.info("Initialized \"user config defaults\": " + str(userConfigDefaults))

class UserConfigApi:
    config_file: Path
    config_as_object: UserConfig
    
    def __init__(self, config_file: Path):
        self.config_file = Path(config_file).expanduser()
        self.idrate_from_disk()
    
    def idrate_from_disk(self):
      """
      Load config file from disk and set config object in instance. 
      If file does not exist, a new one is created with defaults
      """
      logger.info(f"Idrating UserConfig from disk at path: {self.config_file}")
      
      # check if config fil exists
      file_exists = self.config_file.exists()
      
      # if not, create it with defaults
      if not file_exists:
        logger.warning(f"Config not found. Creating a new one with defaults...")
        self.write_config(userConfigDefaults)
        logger.info(f"Config created!")
        
      # read config file and set config object in instance
      logger.info(f"Reading config file...")
      self.read_config()
    
    def read_config(self):
      """Read config file from disk, parse it, and set config object in instance"""
      # get raw json (or fail)
      # rawJson = None
      try:
        with open(self.config_file, "r", encoding="utf-8") as f:
          rawJson = json.load(f)
      except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading config file: {e}")
        raise e
      logger.info(f"Loaded config file as json.")
      
      # parse json to object (or fail)
      # parsedConfig: None | UserConfig = None
      try: 
        parsedConfig = UserConfig(**rawJson)
      except Exception as e:
        logger.error(f"Error parsing config file: {e}")
        raise e
      logger.info(f"Loaded config file as object (parsed with pydantic).")
      
      # set config object in instance
      self.config_as_object = parsedConfig

    def write_config(self, config_as_object: UserConfig) -> None:
        """Write config to file"""
        # ensure parent dir exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        # convert to json
        try:
          data = config_as_object.model_dump()
          # logger.info(f"json: {data}")
        except Exception as e:
          logger.error(f"Error converting config to json: {e}")
          raise e
        # write to file
        try:
          Path(self.config_file).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
          )
        except Exception as e:
          logger.error(f"Error writing config to file: {e}")
          raise e
    
    def get_deep_clone_of_config(self) -> UserConfig:
      """Return a deep clone of the config object"""
      return self.config_as_object.model_copy()
