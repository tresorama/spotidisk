from pydantic import BaseModel
from typing import Optional


class TrackResponse(BaseModel):
    """Single track metadata"""
    spotify_id: str
    title: str
    artists: str
    album: str
    release_date: Optional[str] = None
    duration_ms: int
    preview_url: Optional[str] = None
    cover_url: Optional[str] = None

    # From config
    youtube_url: Optional[str] = None
    label: Optional[str] = None
    disk_file_duration: Optional[int] = None  # milliseconds


class PlaylistResponse(BaseModel):
    """Playlist with all songs"""
    id: str
    name: str
    owner: str
    cover_url: Optional[str] = None
    total_tracks: int
    songs: list[TrackResponse]


class PlaylistListItem(BaseModel):
    """Playlist item for sidebar list"""
    # id: str
    spotify_url: str
    name: str
    # owner: str
    # cover_url: Optional[str] = None
    # total_tracks: int
    # description: Optional[str] = None


class DownloadRequest(BaseModel):
    """Request to download a single track"""
    track_id: str
    playlist_id: str
    youtube_url: Optional[str] = None


class EditMetadataRequest(BaseModel):
    """Request to edit track metadata"""
    track_id: str
    playlist_id: str
    title: Optional[str] = None
    artists: Optional[str] = None
    album: Optional[str] = None
    label: Optional[str] = None


class EditYoutubeUrlRequest(BaseModel):
    """Request to edit YouTube URL"""
    track_id: str
    playlist_id: str
    youtube_url: str


class ClearYoutubeUrlRequest(BaseModel):
    """Request to clear YouTube URL"""
    track_id: str
    playlist_id: str


class SyncPlaylistRequest(BaseModel):
    """Request to sync playlist (download missing tracks)"""
    playlist_id: str


class ID3TagsResponse(BaseModel):
    """ID3 tags for a track"""
    frame_id: str
    tag_name: str
    value: str
    id3_version: str


class ID3TagsUpdateRequest(BaseModel):
    """Request to update ID3 tags"""
    track_id: str
    playlist_id: str
    tags: dict[str, str]
