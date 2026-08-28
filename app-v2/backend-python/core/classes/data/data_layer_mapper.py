import asyncio

from models.playlist import (
  TrackRaw,
  TrackDerived,
  PlaylistRaw,
  PlaylistDerived,
)

from core.classes.data.user_config_api import UserConfigApi
from core.classes.music_providers.utils_track_disk import UtilsTrackDisk
from core.classes.music_providers.utils_track import UtilsTrack
from core.classes.music_providers.utils_spotify import UtilsSpotify
from core.classes.utils.utils_disk import UtilsDisk

class DataLayerMapper:
  @staticmethod
  def mapTrackRawToTrackDerived(trackRaw: TrackRaw, index: int, playlistRaw: PlaylistRaw,userConfigApi: UserConfigApi) -> TrackDerived:
    """Map TrackRaw to TrackDerived"""
    # derive spotify stuff
    spotifyUrl = UtilsSpotify.deriveSpotifyTrackUrlFromId(trackRaw.spotify_id)
    spotifyDurationMs = trackRaw.duration_ms
    spotifyDurationMMSS = UtilsTrack.convertDurationMsToMMSS(spotifyDurationMs)
    
    # derive disk stuff
    # - file path
    diskFileName, diskFileNameWithoutExtension = UtilsTrackDisk.deriveTrackRawFileName(
      trackRaw=trackRaw,
      index=index,
      userConfigApi=userConfigApi,
    )
    diskFilePath, diskFilePathWithoutExtension = UtilsTrackDisk.deriveTrackFilePath(
      trackRaw=trackRaw,
      index=index,
      playlistRaw=playlistRaw,
      userConfigApi=userConfigApi,
    )
    hasDiskFile = UtilsDisk.checkIfFileExists(diskFilePath)
    
    # - if file exists, derive file audio stuff
    diskFileDurationMs: None | int = None
    diskFileDurationMMSS: None | str = None
    if hasDiskFile:
      diskFileDurationMs = UtilsTrackDisk.deriveTrackAudioDurationMs(
        trackRaw=trackRaw,
        index=index,
        playlistRaw=playlistRaw,
        userConfigApi=userConfigApi
      )
      diskFileDurationMMSS = UtilsTrack.convertDurationMsToMMSS(diskFileDurationMs)
      
    return TrackDerived(
      spotify_id= trackRaw.spotify_id,
      spotify_url= spotifyUrl,
      spotify_playlist_id= playlistRaw.spotify_id,
      spotify_preview_url= trackRaw.preview_url,
      spotify_duration_ms= spotifyDurationMs,
      spotify_duration_mm_ss= spotifyDurationMMSS,
      title= trackRaw.title,
      artists= trackRaw.artists,
      album= trackRaw.album,
      release_date= trackRaw.release_date,
      youtube_url= trackRaw.youtube_url,
      cover_url= trackRaw.cover_url,
      recording_label= trackRaw.recording_label,
      disk_file_name= diskFileName,
      disk_file_name_without_extension= diskFileNameWithoutExtension,
      disk_file_path= diskFilePath,
      disk_file_path_without_extension= diskFilePathWithoutExtension,
      has_disk_file= hasDiskFile,
      disk_file_duration_ms= diskFileDurationMs,
      disk_file_duration_mm_ss= diskFileDurationMMSS,
    )
    
  @staticmethod
  def mapTracksRawToTracksDerived(tracksRaw: list[TrackRaw], playlistRaw: PlaylistRaw,userConfigApi: UserConfigApi) -> list[TrackDerived]:
    """Map list of TrackRaw to list of TrackDerived"""
    return [
      DataLayerMapper.mapTrackRawToTrackDerived(
        trackRaw=trackRaw,
        index=index,
        playlistRaw=playlistRaw,
        userConfigApi=userConfigApi
      )
      for index, trackRaw in enumerate(tracksRaw)
    ]
    
  @staticmethod
  def mapTrackDerivedToTrackRaw(trackDerived: TrackDerived) -> TrackRaw:
    """Map TrackDerived to TrackRaw"""
    return TrackRaw(
      spotify_id= trackDerived.spotify_id,
      preview_url= trackDerived.spotify_preview_url,
      title= trackDerived.title,
      artists= trackDerived.artists,
      album= trackDerived.album,
      youtube_url= trackDerived.youtube_url,
      cover_url= trackDerived.cover_url,
      recording_label= trackDerived.recording_label,
      release_date= trackDerived.release_date,
      duration_ms= trackDerived.spotify_duration_ms,
    )
  
  @staticmethod
  def mapPlaylistRawToPlaylistDerived(playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> PlaylistDerived:
    """Map PlaylistRaw to PlaylistDerived"""
    # derive spotify id
    spotifyId = playlistRaw.spotify_id
    spotifyUrl = playlistRaw.spotify_url
    # derive tracks
    tracksRaw=userConfigApi.config_as_object.data_playlists_songs.get(spotifyId, [])
    tracksDerived = DataLayerMapper.mapTracksRawToTracksDerived(tracksRaw, playlistRaw, userConfigApi) 
    tracksCountSpotify = len(tracksDerived)
    tracksCountYoutube = 0
    tracksCountDisk = 0
    
    for trackDerived in tracksDerived:
      hasYoutubeUrl = trackDerived.youtube_url is not None
      hasDiskFile = UtilsDisk.checkIfFileExists(filePath=trackDerived.disk_file_path)
      if hasYoutubeUrl:
        tracksCountYoutube += 1
      if hasDiskFile:
        tracksCountDisk += 1
    
    # derive disk stuff
    dirNameResolved= playlistRaw.directory_name or playlistRaw.name
    diskPath = UtilsTrackDisk.derivePlaylistPath(
      playlistRaw=playlistRaw, 
      userConfigApi=userConfigApi
    )
    # finalize
    derived = PlaylistDerived(
      spotify_id=spotifyId,
      spotify_url=spotifyUrl,
      name=playlistRaw.name,
      enabled=playlistRaw.enabled,
      directory_name=playlistRaw.directory_name,
      disk_path=diskPath,
      lastSpotifyFetchDateTimeISO=playlistRaw.lastSpotifyFetchDateTimeISO,
      directory_name_resolved=dirNameResolved,
      tracks_count=tracksCountSpotify,
      tracks_count_youtube=tracksCountYoutube,
      tracks_count_disk=tracksCountDisk,
      tracks=tracksDerived,
    )
    return derived
  
  @staticmethod
  async def mapTracksRawToTracksDerived_ASYNC(tracksRaw: list[TrackRaw], playlistRaw: PlaylistRaw,userConfigApi: UserConfigApi) -> list[TrackDerived]:
    """Async version of mapTracksRawToTracksDerived"""
    return await asyncio.gather(*[
      asyncio.to_thread(
        DataLayerMapper.mapTrackRawToTrackDerived,
        trackRaw,
        index,
        playlistRaw,
        userConfigApi,
      )
      for index, trackRaw in enumerate(tracksRaw)
    ])
  
  @staticmethod
  async def mapPlaylistRawToPlaylistDerived_ASYNC(playlistRaw: PlaylistRaw, userConfigApi: UserConfigApi) -> PlaylistDerived:
    """Async version of mapPlaylistRawToPlaylistDerived"""
    # derive spotify id
    spotifyId = playlistRaw.spotify_id
    spotifyUrl = playlistRaw.spotify_url
    # derive tracks
    tracksRaw=userConfigApi.config_as_object.data_playlists_songs.get(spotifyId, [])
    tracksDerived = await DataLayerMapper.mapTracksRawToTracksDerived_ASYNC(tracksRaw, playlistRaw, userConfigApi) 
    tracksCountSpotify = len(tracksDerived)
    tracksCountYoutube = 0
    tracksCountDisk = 0
    
    for trackDerived in tracksDerived:
      hasYoutubeUrl = trackDerived.youtube_url is not None
      hasDiskFile = UtilsDisk.checkIfFileExists(filePath=trackDerived.disk_file_path)
      if hasYoutubeUrl:
        tracksCountYoutube += 1
      if hasDiskFile:
        tracksCountDisk += 1
    
    # derive disk stuff
    dirNameResolved= playlistRaw.directory_name or playlistRaw.name
    diskPath = UtilsTrackDisk.derivePlaylistPath(
      playlistRaw=playlistRaw, 
      userConfigApi=userConfigApi
    )
    # finalize
    derived = PlaylistDerived(
      spotify_id=spotifyId,
      spotify_url=spotifyUrl,
      name=playlistRaw.name,
      enabled=playlistRaw.enabled,
      directory_name=playlistRaw.directory_name,
      disk_path=diskPath,
      lastSpotifyFetchDateTimeISO=playlistRaw.lastSpotifyFetchDateTimeISO,
      directory_name_resolved=dirNameResolved,
      tracks_count=tracksCountSpotify,
      tracks_count_youtube=tracksCountYoutube,
      tracks_count_disk=tracksCountDisk,
      tracks=tracksDerived,
    )
    return derived