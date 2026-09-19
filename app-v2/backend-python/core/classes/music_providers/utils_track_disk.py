from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.m4a import M4A
from mutagen.flac import FLAC

from models.playlist import PlaylistRaw, TrackRaw, TrackDerived
from core.classes.data.user_config_api import UserConfigApi
from .utils_track_disk_pure import UtilsTrackDiskPure

class UtilsTrackDisk:
  
  @staticmethod
  def derivePlaylistPath(playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> str:
    """
    Calculate playlist absolute path from `PlaylistRaw`.  
    
    Parameters:
      playlistRaw (PlaylistRaw): instance of `PlaylistRaw`
      userConfigApi (UserConfigApi): instance of `UserConfigApi`
      
    Returns:
      str: playlist absolute path  
      `/Users/username/Music/SpotiDisk/playlistName`
    """
    return UtilsTrackDiskPure.buildPlaylistDirPath(
      playlistDirParentPath=userConfigApi.config_as_object.setting_disk_download_path,
      playlistDirectoryName=playlistRaw.directory_name,
      playlistSpotifyName=playlistRaw.name,
    )
    
  @staticmethod 
  def deriveTrackFileName(title: str, artists: str, index: int, userConfigApi: UserConfigApi):
    """
    Calculate track file name from track metadata (title, artist, index).  
    
    Parameters:
      title (str): track title - `Billie Jean`
      artists (str): track artists - `Michael Jackson, Witney Houston`
      index (int): track index in playlist (input is 0-based, output is 1-based) - `0`
      userConfigApi (UserConfigApi): instance of `UserConfigApi`
      
    Returns:
      output ((str, str)): tuple of `(fileName, fileNameWithoutExtension)`  
      (  
        "01 - Michael Jackson Witney Houston - Billie Jean.mp3",  
        "01 - Michael Jackson Witney Houston - Billie Jean"
      )  
      
    """
    return UtilsTrackDiskPure.buildTrackFileName(
      title=title,
      artists=artists,
      indexInPlaylist=index,
      fileNamePattern=userConfigApi.config_as_object.setting_disk_filename_pattern,
      fileExtension=userConfigApi.config_as_object.setting_disk_format
    )
  
  @staticmethod
  def deriveTrackRawFileName(trackRaw: TrackRaw, index: int, userConfigApi: UserConfigApi): 
    """
    Calculate track file name from `TrackRaw`  
    
    Parameters:
      trackRaw (TrackRaw): instance of `TrackRaw`
      index (int): track index in playlist (input is 0-based, output is 1-based) - `0`
      userConfigApi (UserConfigApi): instance of `UserConfigApi`
      
    Returns:
      output ((str, str)): tuple of `(fileName, fileNameWithoutExtension)`  
      (  
        "01 - Michael Jackson Witney Houston - Billie Jean.mp3",  
        "01 - Michael Jackson Witney Houston - Billie Jean"
      )  
      
    """
    return UtilsTrackDiskPure.buildTrackFileName(
      title=trackRaw.title,
      artists=trackRaw.artists,
      indexInPlaylist=index,
      fileNamePattern=userConfigApi.config_as_object.setting_disk_filename_pattern,
      fileExtension=userConfigApi.config_as_object.setting_disk_format,
    )
  
  @staticmethod
  def deriveTrackFilePath(trackRaw: TrackRaw, index: int, playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi):
    """
    Calculate track absolute file path from TrackRaw and PlaylistRaw.  
    Returns tuple `(finalPathWithExtension, finalPathWithoutExtension)`  
    Example: (  
      `/Users/username/Music/SpotiDisk/playlistName/01 - Artist - Title.mp3`,  
      `/Users/username/Music/SpotiDisk/playlistName/01 - Artist - Title`,  
    )
    """
    playlistPath = UtilsTrackDisk.derivePlaylistPath(
      playlistRaw=playlistRaw, 
      userConfigApi=userConfigApi
    )
    fileNameWithExtension, fileNameWithoutExtension = UtilsTrackDisk.deriveTrackRawFileName(
      trackRaw=trackRaw, 
      index=index, 
      userConfigApi=userConfigApi
    )
    finalPathWithExtension = str(Path(playlistPath, fileNameWithExtension))
    finalPathWithoutExtension = str(Path(playlistPath, fileNameWithoutExtension))
    return (finalPathWithExtension, finalPathWithoutExtension)
  
  @staticmethod
  def deriveTrackAudioDurationMs(trackRaw: TrackRaw, index: int, playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> int:
    """Calculate track audio duration in ms from TrackRaw and PlaylistRaw, returns 0 if file does not exist"""
    # get file
    fileNameString = UtilsTrackDisk.deriveTrackRawFileName(
      trackRaw=trackRaw,
      index=index,
      userConfigApi=userConfigApi
    )[0]
    finalPathString = UtilsTrackDisk.deriveTrackFilePath(
      trackRaw=trackRaw,
      index=index,
      playlistRaw=playlistRaw,
      userConfigApi=userConfigApi
    )[0]
    finalPath = Path(finalPathString).expanduser()
    
    if not finalPath.exists():
      return 0

    duration_sec: int = 0
    ext = fileNameString.split(".")[-1]
    try:
      if ext == 'mp3':
        audio = MP3(finalPath)
        duration_sec = audio.info.length
      elif ext in ['m4a', 'mp4']:
        audio = M4A(finalPath)
        duration_sec = audio.info.length
      elif ext == 'flac':
        audio = FLAC(finalPath)
        duration_sec = audio.info.length
      else:
        return 0
      if duration_sec:
        duration_sec = int(duration_sec * 1000)
      else:
        duration_sec = 0
      return duration_sec
    except Exception:
        return 0
  
  @staticmethod
  def deleteTrackFile(trackDerived: TrackDerived):
    """Delete track file from disk"""
    finalPath = Path(trackDerived.disk_file_path)
    
    # if no file
    if not finalPath.exists():
      return "FILE_NOT_FOUND"
    
    # delete file from disk
    try:
      finalPath.unlink()
    except Exception:
      return "FILE_DELETE_ERROR"
    
    # return
    return "SUCCESS"