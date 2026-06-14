from __future__ import annotations

import json
from pathlib import Path
from core.singleton.logger import logger
from models.new import TrackRaw, UserConfig, PlaylistEditTrackPayload

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
      
    def write_config_to_disk_and_reidrate(self, new_config_as_object: UserConfig) -> None:
      """Write a nw verion of config to disk and refresh instance"""
      self.write_config(new_config_as_object)
      self.idrate_from_disk()
        
    def update_playlist_track(self, update_payload: PlaylistEditTrackPayload):
      """Update track in user config and refresh instance"""
      # create clone of user config
      oldUserConfigObject = self.get_deep_clone_of_config()
      newUserConfigObject = self.get_deep_clone_of_config()
    
      # get current track
      oldConfigTracks = oldUserConfigObject.playlists_songs_data[update_payload.playlist_id]
      oldConfigTrackIndex = next(
        (
          i
          for i, oldConfigTrack in enumerate(oldConfigTracks)
          if oldConfigTrack.spotify_id == update_payload.track_id
        ), 
        None
      )
      oldConfigTrack = oldConfigTracks[oldConfigTrackIndex] if oldConfigTrackIndex != None else None
      # logger.info(f"oldConfigTracks: {oldConfigTracks}")
      # logger.info(f"oldConfigTrackIndex: {oldConfigTrackIndex}")
      # logger.info(f"oldConfigTrack: {oldConfigTrack}")
    
      # if not found, rturn None
      if oldConfigTrackIndex == None or not oldConfigTrack:
        logger.error(f"Track {update_payload.track_id} not found in playlist {update_payload.playlist_id}")
        return None
    
      # create edited version of track
      newConfigTrack = oldConfigTrack.model_copy(deep=True)
      
      # - youtube_url
      if (hasattr(update_payload, "youtube_url")):
        newConfigTrack = TrackRaw(
          **newConfigTrack.model_dump(exclude={"youtube_url"}),
          youtube_url=update_payload.youtube_url,
        )
    
      # save back to user config
      newUserConfigObject.playlists_songs_data[update_payload.playlist_id][oldConfigTrackIndex] = newConfigTrack
      # self.write_config(newUserConfigObject)
      # self.config_as_object = newUserConfigObject
      
      # refresh instance
      self.write_config_to_disk_and_reidrate(newUserConfigObject)
    
      return True

    def update_playlist_tracks(self, playlist_id: str, newTracksRaw: list[TrackRaw]):
      """Update playlist tracks (all tracks of thee playlist) in user config and refresh instance"""
      # create clone of user config
      oldUserConfigObject = self.get_deep_clone_of_config()
      newUserConfigObject = self.get_deep_clone_of_config()
      
      # save back to user config
      newUserConfigObject.playlists_songs_data[playlist_id] = newTracksRaw
      self.write_config_to_disk_and_reidrate(newUserConfigObject)
    
      return True



class UserConfigReaderApi:
  
  @staticmethod
  def getPlaylistRaw(playlist_id: str, userConfigApi: UserConfigApi):
    playlistRaw = next(
      (
      playlist
      for playlist in userConfigApi.config_as_object.saved_playlists
      if playlist.spotify_id == playlist_id
      ), 
      None
    )
    return playlistRaw
    
  @staticmethod
  def getTrackRaw(playlist_id: str, track_id: str, userConfigApi: UserConfigApi):
    playlistRaw = UserConfigReaderApi.getPlaylistRaw(playlist_id, userConfigApi)
    
    if not playlistRaw:
      return None
    
    trackRawIndex = next(
      (
        index
        for index, track in enumerate(userConfigApi.config_as_object.playlists_songs_data[playlist_id])
        if track.spotify_id == track_id
      ),
      None
    )
    
    if trackRawIndex == None:
      return None
    
    trackRaw = userConfigApi.config_as_object.playlists_songs_data[playlist_id][trackRawIndex]
    return trackRaw, playlistRaw, trackRawIndex
    