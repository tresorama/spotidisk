from models.settings import SettingsMutable

from core.classes.data.db import Db
from core.classes.services.service_playlist import ServicePlaylist
from core.classes.utils.utils_disk import UtilsDisk
from core.classes.music_providers.utils_track_disk_pure import UtilsTrackDiskPure
from core.classes.data.user_config_api import UserConfigApi

class ServiceSettings:
  
  def __init__(
    self,
    db: Db,
    servicePlaylist: ServicePlaylist,
    userConfigApi: UserConfigApi,
  ):
    self.db = db
    self.servicePlaylist = servicePlaylist
    self.userConfigApi = userConfigApi
    
  def getSettings(self):
    dbReadResult = self.db.getSettings()
    return (True, "FOUND", dbReadResult)
  
  async def updateSettings(self, payload: SettingsMutable):
    # 1. get current setting (pre-update)
    preUpdateSettingsResult = self.getSettings()
    if preUpdateSettingsResult[0] == False:
      return (False, "DB_READ_ERROR", preUpdateSettingsResult[1])
    preUpdateSettingsMutable = preUpdateSettingsResult[2].mutable
    
    # 2. build final settings mutable
    finalSettingsMutable = payload.model_copy(deep=True)
    
    # 3. do side-effects (and if they fail keep the pre-update settings)
    
    # - if filename pattern changed move playlist track files names
    if payload.setting_disk_filename_pattern != preUpdateSettingsMutable.setting_disk_filename_pattern:
      # get settings
      downloadFolderPath = preUpdateSettingsMutable.setting_disk_download_path
      diskFileExtension = self.userConfigApi.config_as_object.setting_disk_format
      newFileNamePattern = payload.setting_disk_filename_pattern
      # get all PlaylistDerived
      allPlaylistsDerivedResult = await self.servicePlaylist.getPlaylistsDerived()
      if allPlaylistsDerivedResult[0] == True:
        allPlaylistsDerived = allPlaylistsDerivedResult[2]
        # for all playlist...
        for playlistDerived in allPlaylistsDerived:
          playlistDirPath = UtilsTrackDiskPure.buildPlaylistDirPath(
            playlistDirParentPath=downloadFolderPath,
            playlistDirectoryName=playlistDerived.directory_name,
            playlistSpotifyName=playlistDerived.name,
          )
          # ...for each track -> rename file if downloaded
          for (index, trackDerived) in enumerate(playlistDerived.tracks):
            # if track has no disk file -> skip
            if not trackDerived.has_disk_file: continue
            # get old file path
            oldFilePath = trackDerived.disk_file_path
            # calculate new file path
            newFileName, newFileNameWithoutExtension = UtilsTrackDiskPure.buildTrackFileName(
              title=trackDerived.title,
              artists=trackDerived.artists,
              indexInPlaylist=index,
              fileNamePattern=newFileNamePattern,
              fileExtension=diskFileExtension,
            )
            newFilePath = UtilsTrackDiskPure.buildTrackFilePath(
              playlistDirPath=playlistDirPath,
              trackFileName=newFileName,
            )
            # move file
            moveResult = UtilsDisk.moveFileOrDirectory(oldPath=oldFilePath,newPath=newFilePath)
      
    # - if changed download folder path move disk folder
    if payload.setting_disk_download_path != preUpdateSettingsMutable.setting_disk_download_path:
      oldPath = preUpdateSettingsMutable.setting_disk_download_path
      newPath = payload.setting_disk_download_path
      # move only if old dir xists
      oldDirExists = UtilsDisk.checkIfDirExists(dirPath=oldPath)
      if oldDirExists:
        moveResult = UtilsDisk.moveFileOrDirectory(oldPath=oldPath,newPath=newPath)
        if not moveResult:
          # preserve old path
          finalSettingsMutable.setting_disk_download_path = oldPath
        
    
    # 4. update db
    dbUpdateResult = self.db.updateSettings(newSettingsMutable=finalSettingsMutable)
    if dbUpdateResult[0] == False:
      return (False, "DB_UPDATE_ERROR", dbUpdateResult[1])
    return (True, "UPDATED")
  