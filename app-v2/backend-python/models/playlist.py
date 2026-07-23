from typing import Optional
from pydantic import BaseModel, Field
from collections.abc import Sequence

from .examples import EXAMPLE_TRACK_DERIVED, EXAMPLE_PLAYLIST_DERIVED

# ========== Playlist =============

# raw data as saved in persistent storage

class PlaylistRaw(BaseModel):
  """Playlist as saved in persistent storage (config.json file of the user)"""
  spotify_id: str = Field(title="Spotify ID", description="Spotify ID of the playlist, used as Identity", examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
  spotify_url: str = Field(title="Spotify URL", description="Public Spotify URL of the playlist", examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_url])
  name: str = Field(title="Name",description="Name of the playlist (grabbed from Spotify at add time)", examples=[EXAMPLE_PLAYLIST_DERIVED.name])
  enabled: bool = Field(title="Enabled",description="True if playlist is enabled for bulk actions. UNUSED", examples=[EXAMPLE_PLAYLIST_DERIVED.enabled])
  lastSpotifyFetchDateTimeISO: Optional[str] = Field(default=None, title="Last Spotify fetch time",description="Timestamp of last fetch from Spotify. If None, no fetch has been done yet.", examples=[EXAMPLE_PLAYLIST_DERIVED.lastSpotifyFetchDateTimeISO])

class TrackRaw(BaseModel):
  """Track as saved in persistent storage (config.json file of the user)"""
  spotify_id: str = Field(title="Spotify ID", description="Spotify ID of the track, used as Identity", examples=[EXAMPLE_TRACK_DERIVED.spotify_id])
  title: str = Field(title="Title", description="Title of the track", examples=[EXAMPLE_TRACK_DERIVED.title])
  artists: str = Field(title="Artists", description="Artists of the track", examples=[EXAMPLE_TRACK_DERIVED.artists])
  album: str = Field(title="Album", description="Album of the track")
  release_date: str = Field(title="Release date", description="Release date of the track")
  duration_ms: int = Field(title="Duration in ms", description="Duration of the track in ms", examples=[EXAMPLE_TRACK_DERIVED.spotify_duration_ms])
  preview_url: str = Field(title="Preview URL", description="Preview URL of the track from Spotify", examples=[EXAMPLE_TRACK_DERIVED.spotify_preview_url])
  youtube_url: Optional[str] = Field(default=None, title="Youtube URL", description="Youtube URL of the track", examples=[EXAMPLE_TRACK_DERIVED.youtube_url])
  cover_url: Optional[str] = Field(default=None, title="Cover URL", description="Cover URL of the track", examples=[EXAMPLE_TRACK_DERIVED.cover_url])
  recording_label: Optional[str] = Field(default=None, title="Recording label", description="Recording label of the track", examples=[EXAMPLE_TRACK_DERIVED.recording_label])
  
# derived data (raw + computed)

class TrackDerived(BaseModel):
  """TrackRaw plus derived data"""
  spotify_id: str = Field(title="Spotify ID", description="Spotify ID of the track, used as Identity", examples=[EXAMPLE_TRACK_DERIVED.spotify_id])
  spotify_url: str = Field(title="Spotify URL", description="Public Spotify URL of the track", examples=[EXAMPLE_TRACK_DERIVED.spotify_url])
  spotify_playlist_id: str = Field(title="Spotify playlist ID", description="Spotify ID of the playlist the track belongs to", examples=[EXAMPLE_TRACK_DERIVED.spotify_playlist_id])
  spotify_preview_url: str = Field(title="Spotify preview URL", description="Preview URL of the track from Spotify", examples=[EXAMPLE_TRACK_DERIVED.spotify_preview_url])
  spotify_duration_ms: int = Field(title="Spotify duration in ms", description="Duration of the track in ms", examples=[EXAMPLE_TRACK_DERIVED.spotify_duration_ms])
  spotify_duration_mm_ss: str = Field(title="Spotify duration in mm:ss", description="Duration of the track in mm:ss", examples=[EXAMPLE_TRACK_DERIVED.spotify_duration_mm_ss])
  title: str = Field(title="Title", description="Title of the track", examples=[EXAMPLE_TRACK_DERIVED.title])
  artists: str = Field(title="Artists", description="Artists of the track", examples=[EXAMPLE_TRACK_DERIVED.artists])
  album: str = Field(title="Album", description="Album of the track", examples=[EXAMPLE_TRACK_DERIVED.album])
  youtube_url: Optional[str] = Field(default=None, title="Youtube URL", description="Youtube URL of the track", examples=[EXAMPLE_TRACK_DERIVED.youtube_url])
  cover_url: Optional[str] = Field(default=None, title="Cover URL", description="Cover URL of the track", examples=[EXAMPLE_TRACK_DERIVED.cover_url])
  recording_label: Optional[str] = Field(default=None, title="Recording label", description="Recording label of the track", examples=[EXAMPLE_TRACK_DERIVED.recording_label])
  disk_file_name: str = Field(title="Disk file name", description="Name of the disk file", examples=[EXAMPLE_TRACK_DERIVED.disk_file_name])
  disk_file_name_without_extension: str = Field(title="Disk file name without extension", description="Name of the disk file without extension", examples=[EXAMPLE_TRACK_DERIVED.disk_file_name_without_extension])
  disk_file_path: str = Field(title="Disk file path", description="Path of the disk file", examples=[EXAMPLE_TRACK_DERIVED.disk_file_path])
  disk_file_path_without_extension: str = Field(title="Disk file path without extension", description="Path of the disk file without extension", examples=[EXAMPLE_TRACK_DERIVED.disk_file_path_without_extension])
  has_disk_file: bool = Field(title="Has disk file", description="True if the track has a disk file", examples=[EXAMPLE_TRACK_DERIVED.has_disk_file])
  disk_file_duration_ms: Optional[int] = Field(default=None, title="Disk file duration in ms", description="Duration of the disk file in ms", examples=[EXAMPLE_TRACK_DERIVED.disk_file_duration_ms])
  disk_file_duration_mm_ss: Optional[str] = Field(default=None, title="Disk file duration in mm:ss", description="Duration of the disk file in mm:ss", examples=[EXAMPLE_TRACK_DERIVED.disk_file_duration_mm_ss])


class PlaylistDerived(PlaylistRaw):
  """PlaylistRaw plus derived data"""
  spotify_url: str = Field(title="Spotify URL", description="Public Spotify URL of the playlist", examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_url])
  spotify_id: str = Field(title="Spotify ID", description="Spotify ID of the playlist, used as Identity", examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
  lastSpotifyFetchDateTimeISO: Optional[str] = Field(default=None, title="Last fetch date time in ISO", description="Timestamp of last fetch from Spotify. If None, no fetch has been done yet.", examples=[EXAMPLE_PLAYLIST_DERIVED.lastSpotifyFetchDateTimeISO])
  tracks: Sequence[TrackDerived] = Field(title="Tracks", description="List of playlist tracks")
  tracks_count: int = Field(title="Tracks count", description="Number of tracks in the playlist", examples=[EXAMPLE_PLAYLIST_DERIVED.tracks_count])
  disk_path: str = Field(title="Disk path", description="Path of the disk where the playlist tracks files are stored", examples=[EXAMPLE_PLAYLIST_DERIVED.disk_path])

# add

class PlaylistAddPlaylistPayload(BaseModel):
  """Payload for playlistAddOne feature"""
  playlistSpotifyUrl: str = Field(title="Spotify URL",description="Public Spotify URL of the playlist", examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_url])

# edit

class PlaylistEditTrackPayload(BaseModel):
  """Payload for playlistEditTrack feature"""
  playlist_id: str = Field(title="Playlist ID",description="ID of the playlist of the track to edit", examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
  track_id: str = Field(title="Track ID",description="ID of the track to edit", examples=[EXAMPLE_TRACK_DERIVED.spotify_id])
  youtube_url: Optional[str | None] = Field(default=None,title="Youtube URL",description="Youtube URL of the track", examples=[EXAMPLE_TRACK_DERIVED.youtube_url])
  