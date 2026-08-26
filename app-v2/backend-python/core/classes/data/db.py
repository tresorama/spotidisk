from models.playlist import TrackRaw, PlaylistRaw
from models.settings import Settings,SettingsReadonly,SettingsMutable
from models.user_config import UserConfig

from core.classes.config.app_config import AppConfig
from core.classes.utils.utils_native_deps_checker import UtilsNativeDepsChecker

from core.singleton.user_config_api import UserConfigApi

class Db():
  def __init__(
    self, 
    userConfigApi: UserConfigApi,
    appConfig: AppConfig,
    nativeDepsChecker: UtilsNativeDepsChecker
  ):
    self.userConfigApi = userConfigApi
    self.appConfig = appConfig
    self.nativeDepsChecker = nativeDepsChecker
  
  def _getDbSnaphot(self) -> UserConfig:
    return self.userConfigApi.config_as_object.model_copy(deep=True)
  
  def _saveNewDbSnapshot(self, dbSnapshot: UserConfig):
    self.userConfigApi.write_config_to_disk_and_reidrate(new_config_as_object=dbSnapshot)
    
  def getPlaylistsRaw(self):
    """Return all playlists (PlaylistRaw) from user config"""
    dbCopy = self._getDbSnaphot()
    return (True, "FOUND", dbCopy.data_playlists)
  
  def getPlaylistRaw(self, playlist_id: str):
    """Get one playlist (PlaylistRaw) from user config, or None if not found"""
    dbCopy = self._getDbSnaphot()
    playlistRawIndex = next(
      (
      index
      for index, playlist in enumerate(dbCopy.data_playlists)
      if playlist.spotify_id == playlist_id
      ), 
      None
    )
    if playlistRawIndex == None: 
      return (False, "NOT_FOUND")
    playlistRaw = dbCopy.data_playlists[playlistRawIndex]
    return (True, "FOUND", playlistRawIndex, playlistRaw)
  
  def addPlaylistRaw(self, add_payload: PlaylistRaw):
    """Add playlist to user config and refresh instance"""
    newDbSnapshot = self._getDbSnaphot()
    # ensure playlist doesn't already exist
    yetExists = next(
      (
        playlist
        for playlist in newDbSnapshot.data_playlists
        if playlist.spotify_id == add_payload.spotify_id
      ), 
      None
    )
    if yetExists:
      return (False, "ALREADY_EXISTS")
    
    # save back to user config
    newDbSnapshot.data_playlists.append(add_payload)
    self._saveNewDbSnapshot(newDbSnapshot)
    
    return (True, "ADDED")
  
  def deletePlaylistRawAndTracks(self, playlist_id: str):
    """Delete playlist and it's tracks from user config and refresh instance"""
    dbCopy = self._getDbSnaphot()
    # get playlist
    playlistRawResult = self.getPlaylistRaw(playlist_id=playlist_id)
    if playlistRawResult[0] == False:
      return (False, "NOT_FOUND")
    playlistRawIndex = playlistRawResult[2]
    
    # create new db snapshot
    newDbSnapshot = self._getDbSnaphot()
    
    # - delete playlist data
    newDbSnapshot.data_playlists.pop(playlistRawIndex)
    # - delete playlist tracks
    if playlist_id in newDbSnapshot.data_playlists_songs:
      newDbSnapshot.data_playlists_songs.pop(playlist_id)
    
    # save back to user config
    self._saveNewDbSnapshot(newDbSnapshot)
    
    return (True, "DELETED")
  
  def updatePlaylistRawData(self, playlist_id: str, updatedPlaylistRaw: PlaylistRaw):
    """Update playlist data in user config and refresh instance"""
    # get current playlist
    oldPlaylistRawResult = self.getPlaylistRaw(playlist_id=playlist_id)
    if oldPlaylistRawResult[0] == False:
      return (False, "NOT_FOUND")
    oldPlaylistRawIndex = oldPlaylistRawResult[2]
    
    # save back to user config
    newDbSnapshot = self._getDbSnaphot()
    newDbSnapshot.data_playlists[oldPlaylistRawIndex] = updatedPlaylistRaw
    self._saveNewDbSnapshot(newDbSnapshot)
    
    return (True, "UPDATED")
    
  def updatePlaylistTracksRaw(self, playlist_id: str, updatedTracksRaw: list[TrackRaw]):
    """Update playlist data in user config and refresh instance"""
    # get current playlist
    oldPlaylistRawResult = self.getPlaylistRaw(playlist_id=playlist_id)
    if oldPlaylistRawResult[0] == False:
      return (False, "NOT_FOUND")
    oldPlaylistRawIndex = oldPlaylistRawResult[2]
    
    # save back to user config
    newDbSnapshot = self._getDbSnaphot()
    newDbSnapshot.data_playlists_songs[playlist_id] = updatedTracksRaw
    self._saveNewDbSnapshot(newDbSnapshot)
    
    return (True, "UPDATED")
  
  def getTrackRaw(self, playlist_id: str, track_id: str):
    """Get on TrackRaw from db"""
    dbCopy = self._getDbSnaphot()
    trackRawIndex = next(
      (
        index
        for index, track in enumerate(dbCopy.data_playlists_songs[playlist_id])
        if track.spotify_id == track_id
      ), 
      None
    )
    if trackRawIndex == None: 
      return (False, "NOT_FOUND")
    
    trackRaw = dbCopy.data_playlists_songs[playlist_id][trackRawIndex]
    return (True, "FOUND", trackRawIndex, trackRaw)
  
  def updateTrackRawData(self, playlist_id: str, updatedTrackRaw: TrackRaw):
    """Update TrackRaw data in user config and refresh instance"""
    # get current TrackRaw
    oldTrackRawResult = self.getTrackRaw(playlist_id=playlist_id, track_id=updatedTrackRaw.spotify_id)
    if oldTrackRawResult[0] == False:
      return (False, "NOT_FOUND")
    oldTrackRawIndex = oldTrackRawResult[2]
    
    # save back to user config
    newDbSnapshot = self._getDbSnaphot()
    newDbSnapshot.data_playlists_songs[playlist_id][oldTrackRawIndex] = updatedTrackRaw
    self._saveNewDbSnapshot(newDbSnapshot)
    
    return (True, "UPDATED")
  
  def getSettings(self) -> Settings: 
    """Get settings"""
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
    newDbSnapshot = self._getDbSnaphot()
    # mutate
    newDbSnapshot.setting_disk_download_path = newSettingsMutable.setting_disk_download_path
    newDbSnapshot.setting_disk_filename_pattern = newSettingsMutable.setting_disk_filename_pattern
    # save back to user config
    self._saveNewDbSnapshot(newDbSnapshot)
    # ok
    return (True, "UPDATED")
    