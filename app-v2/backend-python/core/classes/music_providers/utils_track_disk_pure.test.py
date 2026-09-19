from .utils_track_disk_pure import UtilsTrackDiskPure

def assertWithPrint(r, e):
  print("\n")
  print(f"R: {r}")
  print(f"E: {e}")
  try:
    assert r == e
    print ("✅ PASS")
  except AssertionError:
    print ("❌ ASSERTION ERROR")
    raise
  
class TestUtilsTrackDiskPure:
  
  def test_buildPlaylistDirPath(self):
    # input = playlistDirectoryName is None 
    assertWithPrint(
      UtilsTrackDiskPure.buildPlaylistDirPath(
        playlistDirParentPath="/Users/username/Music/SpotiDisk",
        playlistDirectoryName=None,
        playlistSpotifyName="MY_PLAYLIST",
      ),
      "/Users/username/Music/SpotiDisk/MY_PLAYLIST"
    )
    
    # input = playlistDirectoryName is not None
    assertWithPrint(
      UtilsTrackDiskPure.buildPlaylistDirPath(
        playlistDirParentPath="/Users/username/Music/SpotiDisk",
        playlistDirectoryName="override",
        playlistSpotifyName="MY_PLAYLIST",
      ),
      "/Users/username/Music/SpotiDisk/override"
    )
    
    # input = playlistDirectoryName contains spaces
    assertWithPrint(
      UtilsTrackDiskPure.buildPlaylistDirPath(
        playlistDirParentPath="/Users/username/Music/SpotiDisk",
        playlistDirectoryName=None,
        playlistSpotifyName="MY PLAYLIST",
      ),
      "/Users/username/Music/SpotiDisk/MY PLAYLIST"
    )
    
  def test_buildTrackFileName(self):
    # input index is 0-based, output index is 1-based
    assertWithPrint(
      UtilsTrackDiskPure.buildTrackFileName(
        title="Test Title",
        artists="Test Artists",
        indexInPlaylist=0,
        fileNamePattern="{index} - {artist} - {title}",
        fileExtension="mp3"
      ),
      (
        "01 - Test Artists - Test Title.mp3",
        "01 - Test Artists - Test Title",
      )
    )
    assertWithPrint(
      UtilsTrackDiskPure.buildTrackFileName(
      title="Test Title",
      artists="Test Artists",
      indexInPlaylist=1,
      fileNamePattern="{index} - {artist} - {title}",
      fileExtension="mp3"
      ),
      (
      "02 - Test Artists - Test Title.mp3",
      "02 - Test Artists - Test Title",
      )
    )
    # input = multiple comma separated artists; output = removed commas
    assertWithPrint(
      UtilsTrackDiskPure.buildTrackFileName(
      title="Test Title",
      artists="Test Artists 1, Test Artists 2",
      indexInPlaylist=0,
      fileNamePattern="{index} - {artist} - {title}",
      fileExtension="mp3"
      ),
      (
      "01 - Test Artists 1 Test Artists 2 - Test Title.mp3",
      "01 - Test Artists 1 Test Artists 2 - Test Title",
      )
    )
    # input = title with special chars; output = sanitized (removed special chars)
    SPECIAL_CHARS = [
      "/", 
      "\\", 
      ":", 
      "*", 
      "?", 
      "\"", 
      "<", 
      ">", 
      "|", 
      "'", 
      "!", 
      ","
    ]
    SPECIAL_CHARS_STR = "".join(SPECIAL_CHARS)
    assertWithPrint(
      UtilsTrackDiskPure.buildTrackFileName(
      title=f"Bang{SPECIAL_CHARS_STR}",
      artists="Test Artists",
      indexInPlaylist=0,
      fileNamePattern="{index} - {artist} - {title}",
      fileExtension="mp3"
      ),
      (
      "01 - Test Artists - Bang.mp3",
      "01 - Test Artists - Bang",
      )
    )
    
  def test_buildTrackFilePath(self):
    assertWithPrint(
      UtilsTrackDiskPure.buildTrackFilePath(
        playlistDirPath="/Users/username/Music/SpotiDisk/MY_PLAYLIST",
        trackFileName="01 - Test Artists - Test Title.mp3",
      ),
      "/Users/username/Music/SpotiDisk/MY_PLAYLIST/01 - Test Artists - Test Title.mp3"
    )