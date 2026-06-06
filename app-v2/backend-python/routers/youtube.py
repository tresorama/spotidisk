from fastapi import APIRouter, HTTPException
from models import EditYoutubeUrlRequest
from core.singleton.logger import logger

router = APIRouter(prefix="/youtube", tags=["youtube"])

# ============================================================================
# YouTube URL endpoints
# ============================================================================

@router.post("/{track_id}/youtube-url")
async def set_youtube_url(track_id: str, request: EditYoutubeUrlRequest):
    """Set YouTube URL for a track"""
    logger.info(f"Set YouTube URL for track {track_id}")
    # TODO: Implement
    return {"status": "updated", "track_id": track_id}


@router.delete("/{track_id}/youtube-url")
async def clear_youtube_url(track_id: str, playlist_id: str):
    """Clear YouTube URL for a track"""
    logger.info(f"Clear YouTube URL for track {track_id}")
    # TODO: Implement
    return {"status": "cleared", "track_id": track_id}


@router.post("/{track_id}/find-youtube")
async def find_youtube_url(track_id: str, playlist_id: str):
    """Find and set YouTube URL for a track"""
    logger.info(f"Find YouTube URL for track {track_id}")
    # TODO: Implement - use yt-dlp to search
    return {"status": "searching", "track_id": track_id}
