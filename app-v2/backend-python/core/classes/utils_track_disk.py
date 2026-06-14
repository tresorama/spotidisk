from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.m4a import M4A
from mutagen.flac import FLAC

from models.new import PlaylistRaw, TrackRaw, TrackDerived
from core.classes.user_config_api import UserConfigApi

class UtilsTrackDisk:
  @staticmethod 
  def deriveTrackFileName(title: str, artists: str, index: int, userConfigApi: UserConfigApi) -> str:
    """Calculate track file name from track metadata (title, artist, index)"""
    fileNamePattern = userConfigApi.config_as_object.filename_pattern
    
    # define a map for all replacements
    title_subs  = {
      "/": "",
      "\\": "",
      ":": "",
      "*": "",
      "?": "",
      "\"": "",
      "<": "",
      ">": "",
      "|": "",
      "'": "",
      "!": "",
      ",": "",
    }
    artists_subs  = {
      "/": "",
      "\\": "",
      ":": "",
      "*": "",
      "?": "",
      "\"": "",
      "<": "",
      ">": "",
      "|": "",
      ",": "",
      "'": "",
      " & ": " ",
      "&": "",
    }
    pattern_subs = {
      "title": "{title}",
      "artist": "{artist}",
      "index": "{index:02d}",
    }
    
    # normalize parts
    clean_title = title
    for k,v in title_subs.items():
      clean_title = clean_title.replace(k,v)
    
    clean_artist = artists
    for k,v in artists_subs.items():
      clean_artist = clean_artist.replace(k,v)

    clean_index = str(index+1).zfill(2)
    clean_extension = "." + userConfigApi.config_as_object.format.replace(".","")
    
    # replace pattern with parts
    finalName = fileNamePattern
    finalName = finalName.replace(pattern_subs['title'], clean_title)
    finalName = finalName.replace(pattern_subs['artist'], clean_artist)
    finalName = finalName.replace(pattern_subs['index'], clean_index)
    finalName = finalName + clean_extension
    
    return finalName
  
  @staticmethod
  def deriveTrackRawFileName(trackRaw: TrackRaw, index: int, userConfigApi: UserConfigApi) -> str: 
    """Calculate track file name from TrackRaw"""
    resolved = UtilsTrackDisk.deriveTrackFileName(
      title=trackRaw.title,
      artists=trackRaw.artists,
      index=index,
      userConfigApi=userConfigApi
    )
    return resolved
  
  @staticmethod
  def derivePlaylistPath(playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> str:
    """Calculate playlist path from PlaylistRaw"""
    clean_name = playlistRaw.name.replace("/","").replace("\\","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","").replace("'","")
    return userConfigApi.config_as_object.download_path + "/" + clean_name
  
  @staticmethod
  def deriveTrackFilePath(trackRaw: TrackRaw, index: int, playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> str:
    """Calculate track file path (absolute path) from TrackRaw and PlaylistRaw"""
    fileName = UtilsTrackDisk.deriveTrackRawFileName(trackRaw, index, userConfigApi)
    playlistPath = UtilsTrackDisk.derivePlaylistPath(playlistRaw, userConfigApi)
    filePath = playlistPath + "/" + fileName
    return filePath
  
  @staticmethod
  def deriveTrackAudioDurationMs(trackRaw: TrackRaw, index: int, playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> int:
    """Calculate track audio duration in ms from TrackRaw and PlaylistRaw, returns 0 if file does not exist"""
    # get file
    fileNameString = UtilsTrackDisk.deriveTrackRawFileName(
      trackRaw=trackRaw,
      index=index,
      userConfigApi=userConfigApi
    )
    finalPathString = UtilsTrackDisk.deriveTrackFilePath(
      trackRaw=trackRaw,
      index=index,
      playlistRaw=playlistRaw,
      userConfigApi=userConfigApi
    )
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