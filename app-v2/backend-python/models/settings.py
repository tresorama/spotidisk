from pydantic import BaseModel, Field
  
class SettingsReadonly(BaseModel):
  """Readonly part of Settings. User cannot change these settings."""
  user_config_file_path: str = Field(title="User config file path", description="Path of the user config file (config.json)", examples=["/Users/username/.config/spotify-disk-downloader/config.json"])
  binary_deno_file_path: str = Field(title="Binary Deno file path", description="Path of the binary Deno file", examples=["/usr/local/bin/deno"])
  binary_ffmpeg_file_path: str = Field(title="Binary Ffmpeg file path", description="Path of the binary Ffmpeg file", examples=["/usr/local/bin/ffmpeg"])
  
class SettingsMutable(BaseModel):
  """Mutable part of Settings. User can change these settings."""
  setting_disk_download_path: str = Field(title="Disk download path", description="Path where to download tracks to. This path is PARENT dir of each playlist dir.", examples=["/Users/username/Music/SpotiDisk"])
  setting_disk_filename_pattern: str = Field(title="Disk filename pattern", description="Filename pattern used to build the file name of the track's disk file", examples=["{index} {artist} - {title}"])

class Settings(BaseModel):
  """Settings of the backed app (mix of user settings and app settings)"""
  readonly: SettingsReadonly = Field(title="Readonly settings", description="Readonly settings. User cannot change these settings.")
  mutable: SettingsMutable = Field(title="Mutable settings", description="Mutable settings. User can change these settings.")
