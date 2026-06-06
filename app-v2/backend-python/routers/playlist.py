from __future__ import annotations
from fastapi import APIRouter, HTTPException
from core.singleton.logger import logger
from core.singleton.config_runtime import config_runtime

router = APIRouter(prefix="/playlists", tags=["playlists"])

# ============================================================================
# Playlists endpoints
# ============================================================================

@router.get("/", response_model=list[PlaylistListItem])
async def list_playlists():
    """List all saved playlists from config"""
    logger.info("Fetching playlists list")
    # TODO: Implement - read from config.json
    return []


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

