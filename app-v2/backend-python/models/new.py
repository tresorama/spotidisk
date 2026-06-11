from typing import Optional
from pydantic import BaseModel, HttpUrl, ConfigDict
from collections.abc import Sequence

# raw data as saved in persistent storage

class PlaylistRaw(BaseModel):
  url: str # spotify url
  name: str
  enabled: bool

class TrackRaw(BaseModel):
  spotify_id: str
  title: str
  artists: str
  album: str
  release_date: str
  duration_ms: int
  youtube_url: Optional[str] = None
  preview_url: Optional[HttpUrl] = None
  disk_file_duration: int
  
class UserConfig(BaseModel):
  model_config = ConfigDict(extra="ignore")
  version: int
  download_path: str
  format: str
  quality: str
  filename_pattern: str
  saved_playlists: list[PlaylistRaw]
  add_meta_tags: bool
  show_preview: bool
  playlists_songs_data: dict[str, list[TrackRaw]]

# derived data (raw + computed)

class TrackDerived(TrackRaw):
  disk_file_path: str

class PlaylistDerived(PlaylistRaw):
  spotify_url: str
  spotify_id: str
  tracks: Sequence[TrackDerived]
  tracks_count: int
