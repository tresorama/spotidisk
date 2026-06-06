from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import settings
from models import (
    PlaylistListItem,
    PlaylistResponse,
    TrackResponse,
    DownloadRequest,
    EditMetadataRequest,
    EditYoutubeUrlRequest,
    ClearYoutubeUrlRequest,
    SyncPlaylistRequest,
    ID3TagsResponse,
    ID3TagsUpdateRequest,
)

# Setup logging
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="Sunnify API",
    description="Spotify & YouTube music downloader",
    version="2.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Playlists endpoints
# ============================================================================

@app.get("/playlists", response_model=list[PlaylistListItem])
async def list_playlists():
    """List all saved playlists from config"""
    logger.info("Fetching playlists list")
    # TODO: Implement - read from config.json
    return []


@app.get("/playlists/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: str):
    """Get playlist with all songs"""
    logger.info(f"Fetching playlist {playlist_id}")
    # TODO: Implement - fetch from Spotify API + merge with config
    raise HTTPException(status_code=404, detail="Playlist not found")


@app.post("/playlists/{playlist_id}/refresh", response_model=PlaylistResponse)
async def refresh_playlist(playlist_id: str):
    """Fetch fresh data from Spotify and merge with local config"""
    logger.info(f"Refreshing playlist {playlist_id}")
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Playlist not found")


# ============================================================================
# Download endpoints
# ============================================================================

@app.post("/download")
async def download_track(request: DownloadRequest):
    """Download single track"""
    logger.info(f"Download request for track {request.track_id}")
    # TODO: Implement - scrape YouTube, write metadata, save to disk
    return {"status": "downloading", "track_id": request.track_id}


@app.post("/sync/{playlist_id}")
async def sync_playlist(playlist_id: str):
    """Sync all missing tracks in playlist"""
    logger.info(f"Sync request for playlist {playlist_id}")
    # TODO: Implement - download all missing tracks
    return {"status": "syncing", "playlist_id": playlist_id}


@app.post("/redownload")
async def redownload_track(request: DownloadRequest):
    """Delete and re-download a track"""
    logger.info(f"Re-download request for track {request.track_id}")
    # TODO: Implement
    return {"status": "redownloading", "track_id": request.track_id}


@app.delete("/tracks/{track_id}")
async def delete_track(track_id: str, playlist_id: str):
    """Delete track file from disk"""
    logger.info(f"Delete request for track {track_id}")
    # TODO: Implement
    return {"status": "deleted", "track_id": track_id}


# ============================================================================
# Metadata endpoints
# ============================================================================

@app.post("/tracks/{track_id}/metadata")
async def update_metadata(track_id: str, request: EditMetadataRequest):
    """Update track metadata (title, artist, album, label)"""
    logger.info(f"Update metadata for track {track_id}")
    # TODO: Implement
    return {"status": "updated", "track_id": track_id}


@app.get("/tracks/{track_id}/tags", response_model=list[ID3TagsResponse])
async def get_id3_tags(track_id: str, playlist_id: str):
    """Get ID3 tags for a track"""
    logger.info(f"Fetching ID3 tags for track {track_id}")
    # TODO: Implement
    return []


@app.post("/tracks/{track_id}/tags")
async def update_id3_tags(track_id: str, request: ID3TagsUpdateRequest):
    """Update ID3 tags for a track"""
    logger.info(f"Update ID3 tags for track {track_id}")
    # TODO: Implement
    return {"status": "updated", "track_id": track_id}


# ============================================================================
# YouTube URL endpoints
# ============================================================================

@app.post("/tracks/{track_id}/youtube-url")
async def set_youtube_url(track_id: str, request: EditYoutubeUrlRequest):
    """Set YouTube URL for a track"""
    logger.info(f"Set YouTube URL for track {track_id}")
    # TODO: Implement
    return {"status": "updated", "track_id": track_id}


@app.delete("/tracks/{track_id}/youtube-url")
async def clear_youtube_url(track_id: str, playlist_id: str):
    """Clear YouTube URL for a track"""
    logger.info(f"Clear YouTube URL for track {track_id}")
    # TODO: Implement
    return {"status": "cleared", "track_id": track_id}


@app.post("/tracks/{track_id}/find-youtube")
async def find_youtube_url(track_id: str, playlist_id: str):
    """Find and set YouTube URL for a track"""
    logger.info(f"Find YouTube URL for track {track_id}")
    # TODO: Implement - use yt-dlp to search
    return {"status": "searching", "track_id": track_id}


# ============================================================================
# WebSocket for real-time updates
# ============================================================================

@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """WebSocket for real-time download progress"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: Implement - send progress updates
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ============================================================================
# Health check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "2.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level,
    )
