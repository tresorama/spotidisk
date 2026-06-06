from fastapi import APIRouter, HTTPException
from models import EditMetadataRequest, ID3TagsResponse, ID3TagsUpdateRequest
from core.logger import logger

router = APIRouter(prefix="/tracks", tags=["tracks"])

# ============================================================================
# Metadata endpoints
# ============================================================================

@router.post("/{track_id}/metadata")
async def update_metadata(track_id: str, request: EditMetadataRequest):
    """Update track metadata (title, artist, album, label)"""
    logger.info(f"Update metadata for track {track_id}")
    # TODO: Implement
    return {"status": "updated", "track_id": track_id}


@router.get("/{track_id}/tags", response_model=list[ID3TagsResponse])
async def get_id3_tags(track_id: str, playlist_id: str):
    """Get ID3 tags for a track"""
    logger.info(f"Fetching ID3 tags for track {track_id}")
    # TODO: Implement
    return []


@router.post("/{track_id}/tags")
async def update_id3_tags(track_id: str, request: ID3TagsUpdateRequest):
    """Update ID3 tags for a track"""
    logger.info(f"Update ID3 tags for track {track_id}")
    # TODO: Implement
    return {"status": "updated", "track_id": track_id}
