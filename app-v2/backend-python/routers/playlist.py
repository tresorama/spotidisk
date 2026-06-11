from __future__ import annotations

from fastapi import APIRouter, HTTPException
from models.new import PlaylistDerived
from core.singleton.logger import logger
from core.classes.user_config_api import UserConfigApi
from core.singleton.config_runtime import config_runtime
from core.classes.utils_spotify import UtilsSpotify
from core.classes.data_layer_mapper import DataLayerMapper

router = APIRouter(prefix="/playlists", tags=["playlists"])
userConfigApi = UserConfigApi(config_runtime.config_file)

# ============================================================================
# Playlists endpoints
# ============================================================================

@router.get("/", response_model=list[PlaylistDerived])
async def list_playlists():
    """List all saved playlists from config"""
    logger.info("Fetching playlists list")
    playlists = userConfigApi.config_as_object.saved_playlists
    # logger.info(f"Playlists: {playlists}")
    playlistsDerived = [
      DataLayerMapper.mapPlaylistRawToPlaylistDerived(playlist, userConfigApi)
      for playlist in playlists
    ]
    logger.info(f"Found {len(playlistsDerived)} raw playlists, and {len(playlistsDerived)} derived playlists.")
    # logger.info(f"Playlists (PlaylistDerived): {playlistsDerived}")
    return playlistsDerived


@router.get("/{playlist_id}", response_model=PlaylistDerived)
async def get_playlist(playlist_id: str):
    """Get single playlist with all songs"""
    # find playlist
    playlistUrl = UtilsSpotify.deriveSpotifyPlaylistUrlFromId(playlist_id)
    logger.info(f"Derived playlist url: id -> url - {playlist_id} -> {playlistUrl}")
    playlistRaw = next((
      item 
      for item in userConfigApi.config_as_object.saved_playlists
      if str(item.url).startswith(playlistUrl)
    ), None)
    if not playlistRaw:
      logger.error(f"Playlist {playlist_id} not found")
      raise HTTPException(status_code=404, detail="Playlist not found")
    # derive PlaylistDerived
    playlistDerived = DataLayerMapper.mapPlaylistRawToPlaylistDerived(playlistRaw, userConfigApi)
    return playlistDerived
  
# @router.post("/{playlist_id}/edit", response_model=PlaylistDerived)
# async def edit_playlist(playlist_id: str, payload: PlaylistEditRequest):
#     """Edit playlist"""
#     logger.info(f"Editing playlist {playlist_id}")
#     prevPlaylistRaw = next((
#       item 
#       for item in userConfigApi.config_as_object.saved_playlists
#       if str(item.url).startswith(playlist_id)
#     ), None)
#     if not prevPlaylistRaw:
#       logger.error(f"Playlist {playlist_id} not found")
#       raise HTTPException(status_code=404, detail="Playlist not found")
#     # update playlist
#     # TODO: Implement
#     raise HTTPException(status_code=404, detail="Playlist not found")

# @router.post("/{playlist_id}/refresh", response_model=PlaylistDerived)
# async def refresh_playlist(playlist_id: str):
#     """Fetch fresh data from Spotify and merge with local config"""
#     logger.info(f"Refreshing playlist {playlist_id}")
#     # TODO: Implement
#     raise HTTPException(status_code=404, detail="Playlist not found")

