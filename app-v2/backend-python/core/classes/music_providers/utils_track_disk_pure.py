from pathlib import Path
from core.classes.utils.utils_disk import UtilsDisk

class UtilsTrackDiskPure:
  @staticmethod
  def buildPlaylistDirPath(
    playlistDirParentPath: str,
    playlistDirectoryName: str | None,
    playlistSpotifyName: str,
  ):
    """
    Build the absolute path to the playlist dir.
    
    Parameters:
      playlistDirParentPath (str): base download absolute path (parent dir of all playlists dirs)
      playlistDirectoryName (str | None): playlistRaw.directory_name
      playlistSpotifyName (str): playlistRaw.name
    
    Returns:
      finalPath (str) : absolute path to the playlist dir  
      `/Users/username/Music/SpotiDisk/playlistName`
    """
    
    dirName = playlistDirectoryName or playlistSpotifyName
    dirName = UtilsDisk.sanitizeNameForFileOrDirectoryNameUse(dirName)
    finalPath = Path(playlistDirParentPath, dirName)
    return str(finalPath)
  
  @staticmethod
  def buildTrackFileName(
    title: str, 
    artists: str, 
    indexInPlaylist: int, 
    fileNamePattern: str, 
    fileExtension: str
  ):
    """
    Calculate track file name from track metadata (title, artist, index). Returns (fileName, fileNameWithoutExtension)
    
    Parameters:
      title (str): track title - `Billie Jean`
      artists (str): track artists - `Michael Jackson, Whitney Houston`
      indexInPlaylist (int): track index in playlist - `0`
      fileNamePattern (str): filename pattern - `{index} {artist} - {title}`
      fileExtension (str): file extension - `mp3`
    
    Returns:
      output (str, str): track file name, track file name without extension  
      (  
      "01 Michael Jackson Whitney Houston - Billie Jean.mp3",  
      "01 Michael Jackson Whitney Houston - Billie Jean"  
      )  
      
    """
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
      "index": "{index}",
    }
    
    # normalize parts
    clean_title = title
    for k,v in title_subs.items():
      clean_title = clean_title.replace(k,v)
    
    clean_artist = artists
    for k,v in artists_subs.items():
      clean_artist = clean_artist.replace(k,v)

    clean_index = str(indexInPlaylist+1).zfill(2)
    clean_extension = "." + fileExtension.replace(".","")
    
    # replace pattern with parts
    finalName = fileNamePattern
    finalName = finalName.replace(pattern_subs['title'], clean_title)
    finalName = finalName.replace(pattern_subs['artist'], clean_artist)
    finalName = finalName.replace(pattern_subs['index'], clean_index)
    
    finalNameWithoutExtension = finalName
    finalNameWithExtension = finalNameWithoutExtension + clean_extension
    
    return (finalNameWithExtension, finalNameWithoutExtension)
    
  @staticmethod
  def buildTrackFilePath(
    playlistDirPath: str, 
    trackFileName: str,
  ):
    """
    Build the absolute path to the track file.
    
    Parameters:
      playlistDirPath (str): absolute path to the playlist dir - `/Users/username/Music/SpotiDisk/playlistName`
      trackFileName (str): track file name - `01 Michael Jackson Whitney Houston - Billie Jean.mp3`
    
    Returns:
      finalPath (str) : absolute path to the track file  
      `/Users/username/Music/SpotiDisk/playlistName/01 Michael Jackson Whitney Houston - Billie Jean.mp3`
    """
    p = Path(playlistDirPath, trackFileName)
    return str(p)
  
