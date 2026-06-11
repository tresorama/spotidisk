from urllib.parse import urlparse

class UtilsSpotify:
  @staticmethod
  def deriveSpotifyPlaylistIdFromUrl(spotify_playlist_url: str) -> str:
    # input: https://open.spotify.com/playlist/6anvql1OK0kBbmX5tyFWYz?si=dauxr8iKRGu9LVClCqi9xg
    # output: 6anvql1OK0kBbmX5tyFWYz
    id = urlparse(spotify_playlist_url).path.split("/")[2]
    return id
  
  @staticmethod
  def deriveSpotifyPlaylistUrlFromId(spotify_playlist_id: str) -> str:
    return f"https://open.spotify.com/playlist/{spotify_playlist_id}"
  