from models.new import TrackRaw, TrackDerived, PlaylistRaw, PlaylistDerived
from core.classes.user_config_api import UserConfigApi
from core.classes.utils_track_disk import UtilsTrackDisk
from core.classes.utils_spotify import UtilsSpotify

class DataLayerMapper:
  @staticmethod
  def mapTrackRawToTrackDerived(trackRaw: TrackRaw, index: int, userConfigApi: UserConfigApi) -> TrackDerived:
    return TrackDerived(
      spotify_id=trackRaw.spotify_id,
      title=trackRaw.title,
      artists=trackRaw.artists,
      album=trackRaw.album,
      release_date=trackRaw.release_date,
      duration_ms=trackRaw.duration_ms,
      youtube_url=trackRaw.youtube_url,
      preview_url=trackRaw.preview_url,
      disk_file_duration=trackRaw.disk_file_duration,
      disk_file_path=UtilsTrackDisk.deriveTrackFilePath(
        title=trackRaw.title,
        artist=trackRaw.artists,
        index=index,
        fileExtension=userConfigApi.config_as_object.format,
        pattern=userConfigApi.config_as_object.filename_pattern
      )
    )
    
  @staticmethod
  def mapTracksRawToTracksDerived(tracksRaw: list[TrackRaw], userConfigApi: UserConfigApi) -> list[TrackDerived]:
    return [
      DataLayerMapper.mapTrackRawToTrackDerived(trackRaw, index, userConfigApi)
      for index, trackRaw in enumerate(tracksRaw)
    ]
    
  @staticmethod
  def mapPlaylistRawToPlaylistDerived(playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> PlaylistDerived:
    # derive spotify id
    spotifyUrl = str(playlistRaw.url) 
    spotifyId = UtilsSpotify.deriveSpotifyPlaylistIdFromUrl(spotifyUrl)
    # derive tracks
    tracksRaw=userConfigApi.config_as_object.playlists_songs_data.get(spotifyId, [])
    tracksDerived = DataLayerMapper.mapTracksRawToTracksDerived(tracksRaw, userConfigApi) 
    tracksCount = len(tracksDerived)
    # finalize
    derived = PlaylistDerived(
      url=spotifyUrl,
      spotify_url=spotifyUrl,
      spotify_id=spotifyId,
      name=playlistRaw.name,
      enabled=playlistRaw.enabled,
      tracks=tracksDerived,
      tracks_count=tracksCount
    )
    return derived