from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.new import TrackRaw, PlaylistDerived, PlaylistEditTrackPayload
from core.singleton.logger import logger
from core.singleton.user_config_api import userConfigApi
from core.classes.user_config_api import UserConfigReaderApi
from core.classes.data_layer_mapper import DataLayerMapper
from core.classes.utils_disk import UtilsDisk
from core.classes.utils_spotify import UtilsSpotify
from core.classes.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi
from core.classes.utils_track_disk import UtilsTrackDisk

router = APIRouter(prefix="/playlists", tags=["playlists"])

# ============================================================================
# Playlists endpoints
# ============================================================================

@router.get("/", response_model=list[PlaylistDerived])
async def list_playlists():
  """List all saved playlists from config"""
  logger.info("Fetching playlists list")
  playlistsRaw = UserConfigReaderApi.getPlaylistsRaw(userConfigApi)
  # logger.info(f"Playlists: {playlists}")
  playlistsDerived = [
    DataLayerMapper.mapPlaylistRawToPlaylistDerived(playlist, userConfigApi)
    for playlist in playlistsRaw
  ]
  logger.info(f"Found {len(playlistsDerived)} raw playlists, and {len(playlistsDerived)} derived playlists.")
  # logger.info(f"Playlists (PlaylistDerived): {playlistsDerived}")
  return playlistsDerived

@router.get("/{playlist_id}", response_model=PlaylistDerived)
async def get_playlist(playlist_id: str):
  """Get single playlist with all songs"""
  # find playlist by id
  playlistRaw = UserConfigReaderApi.getPlaylistRaw(
    playlist_id=playlist_id, 
    userConfigApi=userConfigApi
  )
  if not playlistRaw:
    logger.error(f"Playlist {playlist_id} not found")
    raise HTTPException(status_code=404, detail="Playlist not found")
  # derive PlaylistDerived
  playlistDerived = DataLayerMapper.mapPlaylistRawToPlaylistDerived(
    playlistRaw=playlistRaw, 
    userConfigApi=userConfigApi
  )
  return playlistDerived
  
@router.post("/{playlist_id}/spotify/refetch", response_model=bool)
async def refetch_spotify_side(playlist_id: str):
  """Fetch fresh data from Spotify and merge with local config"""
  logger.info(f"Refreshing playlist {playlist_id}")
  
  # ensure playlist exists in user config
  oldPlaylistRaw = UserConfigReaderApi.getPlaylistRaw(playlist_id, userConfigApi)
  if not oldPlaylistRaw:
    logger.error(f"Playlist {playlist_id} not found in your config")
    raise HTTPException(status_code=404, detail="Playlist not found in your config")
  
  # fetch updated playlist data from Spotify
  freshPlaylistSpotifyData = UtilsSpotify.fetchSpotifyPlaylistTracksAndData(playlist_id)
  if not freshPlaylistSpotifyData:
    logger.error(f"Playlist {playlist_id} not found in Spotify")
    raise HTTPException(status_code=404, detail="Playlist not found in Spotify but is in your config. Maybe you made the playlist private or deleted it from Spotify?")
  
  freshSpotifyPlaylistTracks = freshPlaylistSpotifyData[1]
  # print(freshSpotifyPlaylistMeta)
  # print(freshSpotifyPlaylistTracks[0])
  
  # create new raw data (for user config) 
  newConfigTracks: list[TrackRaw] = []
  for freshSpotifyTrack in freshSpotifyPlaylistTracks:
    oldTrackInConfigData = UserConfigReaderApi.getTrackRaw(
      playlist_id=playlist_id, 
      track_id=freshSpotifyTrack.spotify_id, 
      userConfigApi=userConfigApi
    )
    oldTrackInConfig = oldTrackInConfigData[0] if oldTrackInConfigData else None
    newConfigTrack = TrackRaw(
      spotify_id=freshSpotifyTrack.spotify_id,
      title=freshSpotifyTrack.title,
      artists=freshSpotifyTrack.artists,
      album=freshSpotifyTrack.album or "",
      release_date=freshSpotifyTrack.release_date or "",
      duration_ms=freshSpotifyTrack.duration_ms or 0,
      preview_url=freshSpotifyTrack.preview_url or "",
      youtube_url=oldTrackInConfig.youtube_url if oldTrackInConfig else None,
    )
    logger.info(f"newConfigTrack: {newConfigTrack}")
    newConfigTracks.append(newConfigTrack)
    
  # update playlist to user config
  logger.info(f"json: {newConfigTracks}")
  userConfigApi.update_playlist_tracks(playlist_id, newConfigTracks)
  
  return True

@router.post("/edit-track")
async def edit_track(request: PlaylistEditTrackPayload):
  """Edit track in user config"""
  logger.info(f"Editing track {request.track_id} of playlist {request.playlist_id}, request: {request}")
  
  # update
  result = userConfigApi.update_playlist_track(request)
  
  # if track not found, 404
  if result == None or result != True:
    logger.error(f"Track {request.track_id} not found in playlist {request.playlist_id}")
    raise HTTPException(status_code=404, detail="Track not found")
  
  return True
    
@router.post("/{playlist_id}/track/{track_id}/youtube/auto-search-url", response_model=bool)
async def find_and_set_track_youtube_url(playlist_id: str, track_id: str):
  """Find and set YouTube URL for a track"""
  logger.info(f"Find YouTube URL for track {track_id}")
  
  # get track
  trackRawData = UserConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
    userConfigApi=userConfigApi
  )
  if not trackRawData:
    logger.error(f"Track {track_id} not found in playlist {playlist_id}")
    raise HTTPException(status_code=404, detail="Track not found")
  trackRaw = trackRawData[0]
  
  # find YouTube URL
  youtubeUrl = UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack(trackRaw)
  logger.info(f"Found YouTube URL: {youtubeUrl}")
  if not youtubeUrl:
    logger.error(f"Could not find YouTube URL for track {track_id}")
    raise HTTPException(status_code=500, detail="Could not find YouTube URL")
  
  # update track in config
  updateResult = userConfigApi.update_playlist_track(PlaylistEditTrackPayload(
    playlist_id=playlist_id,
    track_id=track_id,
    youtube_url=youtubeUrl
  ))
  if updateResult != True:
    logger.error(f"Could not update Track {track_id} in playlist {playlist_id}")
    raise HTTPException(status_code=500, detail="Cannot update track")
  
  return updateResult

@router.get("/{playlist_id}/track/{track_id}/disk/get-audio-file", response_class=FileResponse)
async def play_disk_track(playlist_id: str, track_id: str):
  """Play track file from disk"""
  logger.info(f"Play request for track {track_id}")
  
  # get track raw
  trackRawData = UserConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
    userConfigApi=userConfigApi
  )
  if not trackRawData:
    logger.error(f"Track {track_id} not found in playlist {playlist_id}")
    raise HTTPException(status_code=404, detail="Track not found")
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  
  # derive track derived
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
    userConfigApi=userConfigApi
  )
  
  # return file
  return FileResponse(
    path=trackDerived.disk_file_path,
    media_type="audio/mpeg",
    filename="song.mp3",
  )
    
@router.post("/{playlist_id}/track/{track_id}/disk/download", response_model=bool)
async def download_track(playlist_id: str, track_id: str):
  """Download track from YouTube as MP3 and save to disk"""
  logger.info(f"Downloading track {track_id}")
  
  # get track raw
  trackRawData = UserConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
    userConfigApi=userConfigApi
  )
  if not trackRawData:
    logger.error(f"Track {track_id} not found in playlist {playlist_id}")
    raise HTTPException(status_code=404, detail="Track not found")
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  
  # derive track derived
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
    userConfigApi=userConfigApi
  )
  
  # download track
  downloadResult = UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3(trackDerived)
  
  if downloadResult[0] == False and downloadResult[1] == "FFMPEG_NOT_INSTALLED":
    logger.error(f"FFmpeg not installed (Known error)")
    raise HTTPException(status_code=400, detail="Could not download track because FFMPEG is not installed in your system")
  
  if downloadResult[0] == False and downloadResult[1] == "NO_YOUTUBE_URL":
    logger.error(f"Could not find YouTube URL for track {track_id} (Known error)")
    raise HTTPException(status_code=400, detail="Could not find YouTube URL")
  
  if downloadResult[0] == False and downloadResult[1] == "ERROR_DOWNLOADING":
    logger.error(f"Could not download track {track_id} (Known error)")
    logger.error(downloadResult[2])
    raise HTTPException(status_code=500, detail="Could not download track")
  
  if downloadResult[0] != True:
    logger.error(f"Could not download track {track_id} (Unknown error)")
    raise HTTPException(status_code=500, detail="Could not download track (Unknown error)")
  
  return True
  
@router.post("/{playlist_id}/track/{track_id}/disk/delete-file", response_model=bool)
async def delete_track(playlist_id: str, track_id: str):
  """Delete track file from disk"""
  logger.info(f"Delete request for track {track_id}")
  
  # get track raw
  trackRawData = UserConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
    userConfigApi=userConfigApi
  )
  if not trackRawData:
    logger.error(f"Track {track_id} not found in playlist {playlist_id}")
    raise HTTPException(status_code=404, detail="Track not found")
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  
  # derive track derived
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
    userConfigApi=userConfigApi
  )
  
  # delete file
  deletedResult = UtilsTrackDisk.deleteTrackFile(trackDerived)
  
  if deletedResult == "FILE_NOT_FOUND":
    logger.error(f"Track {track_id} not found in playlist {playlist_id}")
    raise HTTPException(status_code=404, detail="File not found in disk")
  
  if deletedResult == "FILE_DELETE_ERROR":
    logger.error(f"Error deleting track {track_id} from playlist {playlist_id}")
    raise HTTPException(status_code=500, detail="Error deleting file from disk")
  
  return True
  
@router.post("/{playlist_id}/disk/reveal-in-finder", response_model=bool)
async def reveal_playlist_folder_on_disk(playlist_id: str):
  """Reveal playlist folder on disk"""
  logger.info(f"Revealing disk for playlist {playlist_id}")
  
  playlistRaw = UserConfigReaderApi.getPlaylistRaw(
    playlist_id=playlist_id,
    userConfigApi=userConfigApi
  )
  if not playlistRaw:
    logger.error(f"Playlist {playlist_id} not found")
    raise HTTPException(status_code=404, detail="Playlist not found")
  
  playlistDerived = DataLayerMapper.mapPlaylistRawToPlaylistDerived(
    playlistRaw=playlistRaw,
    userConfigApi=userConfigApi
  )
  
  UtilsDisk.revealFolderInOS(folderPath=playlistDerived.disk_path)
  return True
  
  
