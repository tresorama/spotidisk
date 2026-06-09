from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from core.singleton.logger import logger
from models.user_config import SchemaUserConfig, SavedPlaylist

logger.info("Initializing user config defaults...")
user_config_deafults = SchemaUserConfig(**{
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
logger.info("user config defaults: " + str(user_config_deafults))

class UserConfigApi:
    config_file: Path
    config_as_object: SchemaUserConfig
    
    def __init__(self, config_file: Path):
        self.config_file = Path(config_file).expanduser()
        self.idrate_from_disk()
    
    def idrate_from_disk(self):
      """Load config file from disk if it exists, otherwise create a new one"""
      file_exists = self.config_file.exists()
      
      if not file_exists:
        logger.warning(f"Config file not found: {self.config_file}")
        logger.warning(f"Creating brand new config file at: {self.config_file}")
        self.write_config(user_config_deafults)
      
      logger.info(f"Config file found: {self.config_file}")
      logger.info(f"Loading config file from: {self.config_file}")
      try:
          with open(self.config_file, "r", encoding="utf-8") as f:
              config_as_json = json.load(f)
              # logger.info(f"Config file loaded: {config_as_json}")
          if isinstance(config_as_json, dict):
              self.config_as_object = SchemaUserConfig(**config_as_json)
              return
          return
      except (json.JSONDecodeError, IOError) as e:
          logger.error(f"Error loading config file: {e}")
          raise e

    def write_config(self, config_as_objetc: SchemaUserConfig) -> None:
        """Write config to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_as_objetc, f, indent=2)
        except IOError as e:
            logger.error(f"Error writing config file: {e}")
    
    # def get_playlists(self) -> list[SavedPlaylist]:
    #     """Get all saved playlists"""
    #     self._load_config()
    #     if self._config_as_object is None:
    #         return []
    #     return self._config_as_object.saved_playlists

    # def get_playlist_songs(self, playlist_id: str) -> list[dict]:
    #     """Get songs for a specific playlist"""
    #     config = self._load_config()
    #     playlists_data = config.get("playlists_songs_data", {})
    #     return playlists_data.get(playlist_id, [])

    # def find_playlist(self, playlist_id: str) -> Optional[dict]:
    #     """Find a playlist by ID"""
    #     playlists = self.get_playlists()
    #     for playlist in playlists:
    #         if playlist.get("id") == playlist_id or playlist.get("url", "").endswith(playlist_id):
    #             return playlist
    #     return None

    # def save_playlist_songs(self, playlist_id: str, songs: list[dict]) -> None:
    #     """Save songs for a playlist"""
    #     config = self._load_config()
    #     if "playlists_songs_data" not in config:
    #         config["playlists_songs_data"] = {}
    #     config["playlists_songs_data"][playlist_id] = songs
    #     self._write_config(config)

    
