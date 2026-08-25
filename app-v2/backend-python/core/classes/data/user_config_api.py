from __future__ import annotations
import json
from pathlib import Path

from models.playlist import PlaylistEditPlaylistPayload, TrackRaw, PlaylistRaw, PlaylistEditTrackPayload
from models.settings import Settings,SettingsReadonly,SettingsMutable
from models.user_config import UserConfig

from core.classes.logger.logger import Logger
from core.classes.config.app_config import AppConfig
from core.classes.utils.utils_native_deps_checker import UtilsNativeDepsChecker
from core.classes.utils.utils_os import UtilsOS
from core.classes.utils.utils_disk import UtilsDisk
from core.classes.music_providers.utils_youtube import UtilsYoutube

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
    
    
class UserConfigReaderApi:
  def __init__(
    self, 
    logger: Logger,
    userConfigApi: UserConfigApi,
    appConfig: AppConfig,
    nativeDepsChecker: UtilsNativeDepsChecker,
  ):
    self.logger: Logger = logger
    self.userConfigApi: UserConfigApi = userConfigApi
    self.appConfig: AppConfig = appConfig
    self.nativeDepsChecker: UtilsNativeDepsChecker = nativeDepsChecker
    
  def getPlaylistsRaw(self) -> list[PlaylistRaw]:
    """Return all playlists (PlaylistRaw) from user config"""
    return self.userConfigApi.config_as_object.data_playlists
  
  def getPlaylistRaw(self, playlist_id: str) -> PlaylistRaw | None:
    """Get one playlist (PlaylistRaw) from user config, or None if not found"""
    playlistRaw = next(
      (
      playlist
      for playlist in self.userConfigApi.config_as_object.data_playlists
      if playlist.spotify_id == playlist_id
      ), 
      None
    )
    return playlistRaw
    
  def getTrackRaw(self, playlist_id: str, track_id: str):
    """Get one track (TrackRaw) from user config, or None if not found"""
    playlistRaw = self.getPlaylistRaw(
      playlist_id=playlist_id,
    )
    
    if not playlistRaw:
      return None
    
    playlistSongsData = self.userConfigApi.config_as_object.data_playlists_songs.get(playlist_id, [])
    trackRawIndex = next(
      (
        index
        for index, track in enumerate(playlistSongsData)
        if track.spotify_id == track_id
      ),
      None
    )
    
    if trackRawIndex == None:
      return None
    
    trackRaw = self.userConfigApi.config_as_object.data_playlists_songs[playlist_id][trackRawIndex]
    return trackRaw, playlistRaw, trackRawIndex
    
  def getSettings(self) -> Settings: 
    """Get settings from user config"""
    return Settings(
      readonly=SettingsReadonly(
        user_config_file_path=str(self.appConfig.runtime.user_config_file_path),
        binary_deno_file_path=self.nativeDepsChecker.getDenoPath() or '-',
        binary_ffmpeg_file_path=self.nativeDepsChecker.getFFmpegPath() or '-',
      ),
      mutable=SettingsMutable(
        setting_disk_download_path=self.userConfigApi.config_as_object.setting_disk_download_path,
        setting_disk_filename_pattern=self.userConfigApi.config_as_object.setting_disk_filename_pattern
      ),
    )
    
  def updateSettings(self, newSettingsMutable: SettingsMutable):
    """Update settings in user config and refresh instance"""
    # create clone of user config
    newUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    
    # mutate
    newUserConfigObject.setting_disk_download_path = newSettingsMutable.setting_disk_download_path
    newUserConfigObject.setting_disk_filename_pattern = newSettingsMutable.setting_disk_filename_pattern
    
    # save back to user config
    self.userConfigApi.write_config_to_disk_and_reidrate(newUserConfigObject)
  
    return True
    
  def addPlaylist(self, add_payload: PlaylistRaw):
    """Add playlist to user config and refresh instance"""
    # create clone of user config
    oldUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    newUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
  
    # if already exists, return None
    yetExists = next(
      (
        playlist
        for playlist in oldUserConfigObject.data_playlists
        if playlist.spotify_id == add_payload.spotify_id
      ), 
      None
    )
    if yetExists:
      return (False, "Playlist already exists")
    
    # initialize playlist data
    newPlaylistRaw = add_payload.model_copy(deep=True)
    newPlaylistRaw.directory_name = UtilsDisk.sanitizeNameForFileOrDirectoryNameUse(
      newPlaylistRaw.directory_name or newPlaylistRaw.name
    )
    
    # save back to user config
    newUserConfigObject.data_playlists.append(newPlaylistRaw)
    self.userConfigApi.write_config_to_disk_and_reidrate(newUserConfigObject)
  
    return (True, "Playlist added")
    
  def updatePlaylist(self, update_payload: PlaylistRaw):
    """Update playlist in user config and refresh instance"""
    # create clone of user config
    oldUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    newUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
  
    # get current playlist
    oldConfigPlaylistIndex = next(
      (
        i
        for i, oldConfigPlaylist in enumerate(oldUserConfigObject.data_playlists)
        if oldConfigPlaylist.spotify_id == update_payload.spotify_id
      ), 
      None
    )
    
    # if not found, rturn None
    if oldConfigPlaylistIndex == None:
      return (False, "Playlist not found")
    
    # save back to user config
    newUserConfigObject.data_playlists[oldConfigPlaylistIndex] = update_payload
    self.userConfigApi.write_config_to_disk_and_reidrate(newUserConfigObject)
  
    return (True, "Playlist updated")
  
  def updatePlaylistData(self, update_payload: PlaylistEditPlaylistPayload):
    """Update playlist data in user config and refresh instance"""
    # create clone of user config
    oldUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    newUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
  
    # get current playlist
    oldConfigPlaylistIndex = next(
      (
        i
        for i, oldConfigPlaylist in enumerate(oldUserConfigObject.data_playlists)
        if oldConfigPlaylist.spotify_id == update_payload.playlist_id
      ), 
      None
    )
    
    oldConfigPlaylist = oldUserConfigObject.data_playlists[oldConfigPlaylistIndex] if oldConfigPlaylistIndex != None else None
    
    # if not found, return None
    if not oldConfigPlaylist or oldConfigPlaylistIndex == None:
      return (False, "Playlist not found")
    
    # create edited playlist
    newConfigPlaylist = oldConfigPlaylist.model_copy(deep=True)
    
    # mutate
    if update_payload.directory_name != None:
      oldDirName = oldConfigPlaylist.directory_name or oldConfigPlaylist.name
      newDirName = update_payload.directory_name
      oldPath = self.userConfigApi.config_as_object.setting_disk_download_path + "/" + oldDirName
      newPath = self.userConfigApi.config_as_object.setting_disk_download_path + "/" + newDirName
      oldExists = UtilsDisk.checkIfFileExists(oldPath)
      if oldExists:
        diskMoveResult = UtilsDisk.moveFileOrDirectory(
          oldPath=oldPath,
          newPath=newPath,
        )
        if diskMoveResult:
          newConfigPlaylist.directory_name = newDirName
      else:
        newConfigPlaylist.directory_name = newDirName
    
    # save back to user config
    newUserConfigObject.data_playlists[oldConfigPlaylistIndex] = newConfigPlaylist
    self.userConfigApi.write_config_to_disk_and_reidrate(newUserConfigObject) 
    
    return (True, "Playlist updated")
  
  def updatePlaylistTrack(self, update_payload: PlaylistEditTrackPayload):
    """Update track in user config and refresh instance"""
    # create clone of user config
    oldUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    newUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
  
    # get current track
    oldConfigTracks = oldUserConfigObject.data_playlists_songs[update_payload.playlist_id]
    oldConfigTrackIndex = next(
      (
        i
        for i, oldConfigTrack in enumerate(oldConfigTracks)
        if oldConfigTrack.spotify_id == update_payload.track_id
      ), 
      None
    )
    oldConfigTrack = oldConfigTracks[oldConfigTrackIndex] if oldConfigTrackIndex != None else None
    # self.logger.info(f"oldConfigTracks: {oldConfigTracks}")
    # self.logger.info(f"oldConfigTrackIndex: {oldConfigTrackIndex}")
    # self.logger.info(f"oldConfigTrack: {oldConfigTrack}")
  
    # if not found, rturn None
    if oldConfigTrackIndex == None or not oldConfigTrack:
      self.logger.error(f"Track {update_payload.track_id} not found in playlist {update_payload.playlist_id}")
      return None
  
    # create edited version of track
    newConfigTrack = oldConfigTrack.model_copy(deep=True)
    
    # - youtube_url
    if (hasattr(update_payload, "youtube_url")):
      if update_payload.youtube_url == None:
        newConfigTrack = TrackRaw(
          **newConfigTrack.model_dump(exclude={"youtube_url"}),
          youtube_url=None,
        )
      else:
        youtubeUrlNormalized = UtilsYoutube.cleanYoutubeVideoUrl(update_payload.youtube_url)
        newConfigTrack = TrackRaw(
          **newConfigTrack.model_dump(exclude={"youtube_url"}),
          youtube_url=youtubeUrlNormalized,
        )
  
    # save back to user config
    newUserConfigObject.data_playlists_songs[update_payload.playlist_id][oldConfigTrackIndex] = newConfigTrack
    # self.write_config(newUserConfigObject)
    # self.config_as_object = newUserConfigObject
    
    # refresh instance
    self.userConfigApi.write_config_to_disk_and_reidrate(newUserConfigObject)
  
    return True
    
  def updatePlaylistTracks(self, playlist_id: str, newTracksRaw: list[TrackRaw]):
    """Update playlist tracks (all tracks of thee playlist) in user config and refresh instance"""
    # create clone of user config
    oldUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    newUserConfigObject = self.userConfigApi.get_deep_clone_of_config()
    
    # save back to user config
    newUserConfigObject.data_playlists_songs[playlist_id] = newTracksRaw
    self.userConfigApi.write_config_to_disk_and_reidrate(newUserConfigObject)
  
    return True


