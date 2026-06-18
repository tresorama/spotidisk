from typing import Literal, Optional, Union
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict, Field
from collections.abc import Sequence

# raw data as saved in persistent storage

class PlaylistRaw(BaseModel):
  spotify_id: str
  spotify_url: str
  name: str
  enabled: bool

class TrackRaw(BaseModel):
  spotify_id: str
  title: str
  artists: str
  album: str
  release_date: str
  duration_ms: int
  preview_url: str
  youtube_url: Optional[str] = None
  
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

class TrackDerived(BaseModel):
  spotify_id: str
  spotify_url: str
  spotify_playlist_id: str
  spotify_preview_url: str
  spotify_duration_ms: int
  spotify_duration_mm_ss: str
  title: str
  artists: str
  album: str
  youtube_url: Optional[str] = None
  disk_file_name: str
  disk_file_name_without_extension: str
  disk_file_path: str
  disk_file_path_without_extension: str
  has_disk_file: bool
  disk_file_duration_ms: Optional[int] = None
  disk_file_duration_mm_ss: Optional[str] = None


class PlaylistDerived(PlaylistRaw):
  spotify_url: str
  spotify_id: str
  tracks: Sequence[TrackDerived]
  tracks_count: int
  disk_path: str


# edit

class PlaylistEditTrackPayload(BaseModel):
  playlist_id: str
  track_id: str
  youtube_url: Optional[str | None] = None
  
  
# ws (websocket) - v2

class WsBackendEventPayloadTypeMessage(BaseModel):
  kind: Literal["MESSAGE"] = "MESSAGE"
  text: str
  severity: Literal[
    "INFO",
    "WARNING",
    "ERROR",
    "SUCCESS",
  ] = "INFO"

class WsBackendEventPayloadTypeFrontendQueryInvalidation(BaseModel):
  kind: Literal["FRONTEND_QUERY_INVALIDATION"] = "FRONTEND_QUERY_INVALIDATION"
  queryKeys: list[str]
  
class FrontendQueryKeys: 
  PLAYLIST_ALL = ['playlists']
  @staticmethod
  def PLAYLIST_DETAILS(playlist_id: str): return ['playlists', playlist_id]

  
class WsBackendEventPayloadTypeJobProgressJobItem(TypedDict):
  title: str
  executionStatus: Literal[
    "WAITING_START",
    "RUNNING",
    "COMPLETED",
    "CANCELED",
    "ERRORED",
  ]
  progress: float
  stepsTotal: int
  stepsCompleted: int
  messages: list[str]
    
class WsBackendEventPayloadTypeJobProgress(BaseModel):
  kind: Literal["JOB_PROGRESS"] = "JOB_PROGRESS"
  dateTimeISO: str
  jobs: list[WsBackendEventPayloadTypeJobProgressJobItem]
  
WsBackendEventPayload = Union[
  WsBackendEventPayloadTypeMessage, 
  WsBackendEventPayloadTypeFrontendQueryInvalidation,
  WsBackendEventPayloadTypeJobProgress,
]

class WsBackendEvent(BaseModel):
  dateTimeISO: str
  payload: WsBackendEventPayload = Field(discriminator="kind")
