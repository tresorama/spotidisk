from pydantic import BaseModel, ConfigDict, Field

from .playlist import PlaylistRaw, TrackRaw

class UserConfig(BaseModel):
  """User Config data as saved in persistent storage (config.json file of the user)"""
  model_config = ConfigDict(extra="ignore")
  
  version: int = Field(title="Version", description="Version of the config")
  setting_disk_download_path: str = Field(title="Disk download path", description="Path where to download tracks to. This path is PARENT dir of each playlist dir.")
  setting_disk_format: str = Field(title="Disk format", description="Format of the disk file")
  setting_disk_quality: str = Field(title="Disk quality", description="Quality of the disk file")
  setting_disk_filename_pattern: str = Field(title="Disk filename pattern", description="Filename pattern used to build the file name of the track's disk file")
  setting_disk_add_meta_tags: bool = Field(title="Add meta tags", description="Add meta tags to the disk file")
  data_playlists: list[PlaylistRaw] = Field(title="Playlists", description="List of playlists")
  data_playlists_songs: dict[str, list[TrackRaw]] = Field(title="Tracks", description="List of playlist tracks, grouped by playlist ID")
