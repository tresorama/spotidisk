from fastapi import APIRouter, HTTPException
from models import DownloadRequest
from core.singleton.logger import logger


router = APIRouter(prefix="/disk", tags=["disk"])

# ============================================================================
# Download endpoints
# ============================================================================

@router.post("/download")
async def download_track(request: DownloadRequest):
    """Download single track"""
    logger.info(f"Download request for track {request.track_id}")
    # TODO: Implement - scrape YouTube, write metadata, save to disk
    return {"status": "downloading", "track_id": request.track_id}


@router.post("/sync/{playlist_id}")
async def sync_playlist(playlist_id: str):
    """Sync all missing tracks in playlist"""
    logger.info(f"Sync request for playlist {playlist_id}")
    # TODO: Implement - download all missing tracks
    return {"status": "syncing", "playlist_id": playlist_id}


@router.post("/redownload")
async def redownload_track(request: DownloadRequest):
    """Delete and re-download a track"""
    logger.info(f"Re-download request for track {request.track_id}")
    # TODO: Implement
    return {"status": "redownloading", "track_id": request.track_id}


@router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, playlist_id: str):
    """Delete track file from disk"""
    logger.info(f"Delete request for track {track_id}")
    # TODO: Implement
    return {"status": "deleted", "track_id": track_id}

