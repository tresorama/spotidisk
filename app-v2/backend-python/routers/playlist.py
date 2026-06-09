from __future__ import annotations

from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse
from models.old import PlaylistListItem, PlaylistResponse, TrackResponse
from models.derived import DerivedPlaylist
from core.singleton.logger import logger
from core.classes.user_config_api import UserConfigApi
from core.singleton.config_runtime import config_runtime
from core.classes.utils_spotify import UtilsSpotify

router = APIRouter(prefix="/playlists", tags=["playlists"])
user_config_api = UserConfigApi(config_runtime.config_file)

# ============================================================================
# Playlists endpoints
# ============================================================================

@router.get("/", response_model=list[DerivedPlaylist])
async def list_playlists():
    """List all saved playlists from config"""
    logger.info("Fetching playlists list")
    playlists = user_config_api.config_as_object.saved_playlists
    logger.info(f"Found {len(playlists)} Playlists: {playlists}")
    playlists_augmented: list[DerivedPlaylist] = []
    for playlist in playlists:
      # https://open.spotify.com/playlist/6anvql1OK0kBbmX5tyFWYz?si=dauxr8iKRGu9LVClCqi9xg
      spotify_url = str(playlist.url) 
      # 6anvql1OK0kBbmX5tyFWYz
      spotify_id = UtilsSpotify.deriveSpotifyPlaylistIdFromUrl(spotify_url)
      tracks=user_config_api.config_as_object.playlists_songs_data.get(spotify_id, [])
      tracks_count = len(tracks)
      derived = DerivedPlaylist(
        spotify_url=spotify_url,
        spotify_id=spotify_id,
        name=playlist.name,
        enabled=playlist.enabled,
        tracks=tracks,
        tracks_count=tracks_count
      )
      playlists_augmented.append(derived)
    logger.info(f"Returning {len(playlists_augmented)} Playlists: {playlists_augmented}")
    return playlists_augmented


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: str):
    """Get playlist with all songs"""
    logger.info(f"Fetching playlist {playlist_id}")
    # TODO: Implement - fetch from Spotify API + merge with config
    raise HTTPException(status_code=404, detail="Playlist not found")


@router.post("/{playlist_id}/refresh", response_model=PlaylistResponse)
async def refresh_playlist(playlist_id: str):
    """Fetch fresh data from Spotify and merge with local config"""
    logger.info(f"Refreshing playlist {playlist_id}")
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Playlist not found")

