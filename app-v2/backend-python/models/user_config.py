from typing import Optional
from pydantic import BaseModel, HttpUrl, ConfigDict


class SavedPlaylist(BaseModel):
    url: HttpUrl
    name: str
    enabled: bool


class Track(BaseModel):
    spotify_id: str

    # presente solo in alcune playlist
    track_url: Optional[HttpUrl] = None

    title: str
    artists: str
    album: str
    release_date: str

    duration_ms: int

    youtube_url: Optional[str] = None
    preview_url: Optional[HttpUrl] = None

    disk_file_duration: int


class SchemaUserConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: int
    download_path: str

    format: str
    quality: str

    filename_pattern: str

    saved_playlists: list[SavedPlaylist]

    add_meta_tags: bool
    show_preview: bool

    playlists_songs_data: dict[str, list[Track]]
    
    
