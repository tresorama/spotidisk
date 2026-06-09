from urllib.parse import urlparse

class UtilsSpotify:
  @staticmethod
  def deriveSpotifyPlaylistIdFromUrl(spotify_playlist_url: str) -> str:
    id = urlparse(spotify_playlist_url).path.split("/")[2]
    return id
  
  @staticmethod
  def deriveSpotifyPlaylistUrlFromId(spotify_playlist_id: str) -> str:
    return f"https://open.spotify.com/playlist/{spotify_playlist_id}"