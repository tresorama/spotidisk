from __future__ import annotations
from fastapi import APIRouter, Path as FastApiPath
from fastapi.responses import FileResponse

from ..spec.openapi import OPENAPI_TAG_NAME
from ..routers_types.playlists import (
  PlaylistDiskDeleteTrackFile_ResponseError500,
  PlaylistDiskDownloadSingleTrack_ResponseError500,
  PlaylistGetAll_Response200,
  PlaylistGetOne_Response200,
  PlaylistGetOne_ResponseError404,
  PlaylistAddOne_RequestBody,
  PlaylistAddOne_Response200,
  PlaylistAddOne_ResponseError404,
  PlaylistAddOne_ResponseError500,
  PlaylistSpotifyRefetchPlaylist_Response200,
  PlaylistSpotifyRefetchPlaylist_ResponseError404,
  PlaylistEditTrack_RequestBody,
  PlaylistEditTrack_Response200,
  PlaylistEditTrack_ResponseError404,
  PlaylistYoutubeAutoSearchUrlSingleTrack_Response200,
  PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError404,
  PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500,
  PlaylistYoutubeAutoSearchUrlAllTracks_Response200,
  PlaylistYoutubeAutoSearchUrlAllTracks_ResponseError404,
  PlaylistDiskGetAudioFile_Response200,
  PlaylistDiskGetAudioFile_ResponseError404,
  PlaylistDiskDownloadSingleTrack_Response200,
  PlaylistDiskDownloadSingleTrack_ResponseError404,
  PlaylistDiskDownloadAllTracks_Response200,
  PlaylistDiskDownloadAllTracks_ResponseError404,
  PlaylistDiskDeleteTrackFile_Response200,
  PlaylistDiskDeleteTrackFile_ResponseError404,
)

from models.playlist import PlaylistRaw, TrackRaw, PlaylistEditTrackPayload
from models.ws import WsBackendEventPayloadTypeMessage
from models.examples import EXAMPLE_TRACK_DERIVED,EXAMPLE_PLAYLIST_DERIVED

from core.singleton.logger import loggerHTTP as logger
from core.singleton.user_config_api import userConfigReaderApi, userConfigApi
from core.singleton.job_queue import jobQueue
from core.singleton.websocket_event_emitter import webSocketEventEmitter

from core.classes.data.data_layer_mapper import DataLayerMapper
from core.classes.operations.utils_operations import UtilsOperations
from core.classes.music_providers.utils_spotify import UtilsSpotify
from core.classes.music_providers.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi
from core.classes.music_providers.utils_track_disk import UtilsTrackDisk
from core.classes.utils.utils_time import UtilsTime, UtilsTimeExecutionTimer

router = APIRouter(
  prefix="/playlists", 
  tags=[OPENAPI_TAG_NAME.PLAYLIST],
)

# ============================================================================
# Playlists endpoints
# ============================================================================


@router.get("/", 
            operation_id="playlistGetAll", 
            summary="Get all playlists",
            description="Get all saved playlists (PlaylistRaw) from user config",
            )
async def playlists_getAll() -> PlaylistGetAll_Response200:
  logger.info("Fetching playlists list...")
  
  # get from db
  timerGetDb = UtilsTimeExecutionTimer()
  
  playlistsRaw = userConfigReaderApi.getPlaylistsRaw()
  
  timeGetDb = timerGetDb.end()
  logger.info(f"Got {len(playlistsRaw)} raw playlists from DB! Read Time: {timeGetDb}!")
  return playlistsRaw

@router.get("/{playlist_id}", 
            operation_id="playlistGetOne", 
            summary="Get single playlist",
            description="Get single playlist (PlaylistDerived) from user config",
            responses={
              404: { "model": PlaylistGetOne_ResponseError404 },
            },
            )
async def playlist_getOne(
  playlist_id: str = FastApiPath(description="Spotify playlist id",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistGetOne_Response200:
  # find playlist by id
  timerGetDb = UtilsTimeExecutionTimer()
  
  playlistRaw = userConfigReaderApi.getPlaylistRaw(
    playlist_id=playlist_id, 
  )
  timeGetDb = timerGetDb.end()
  
  if not playlistRaw:
    logger.error(f"Playlist {playlist_id} not found. Read time: {timeGetDb}")
    raise PlaylistGetOne_ResponseError404(message=f"Playlist {playlist_id} not found").toHttpException()
  
  # derive PlaylistDerived
  timerDerive = UtilsTimeExecutionTimer()
  
  playlistDerived = await DataLayerMapper.mapPlaylistRawToPlaylistDerived_ASYNC(
    userConfigApi=userConfigApi,
    playlistRaw=playlistRaw, 
  )
  
  timeDerive = timerDerive.end()
  logger.info(f"Playlist {playlist_id} derived! Read time: {timeGetDb} | Derive time: {timeDerive}")
  
  return playlistDerived
  
@router.post("/add", 
             operation_id="playlistAddOne", 
             summary="Add new playlist",
             description="Add new playlist to user config by spotify playlist url",
             responses={
               404: { "model": PlaylistAddOne_ResponseError404 },
               500: { "model": PlaylistAddOne_ResponseError500 },
             }
             )
async def playlist_addOne(
  request: PlaylistAddOne_RequestBody
) -> PlaylistAddOne_Response200:
  # derive playlist spotify id
  playlistId = UtilsSpotify.deriveSpotifyPlaylistIdFromUrl(request.playlistSpotifyUrl)
  playlistUrl = UtilsSpotify.deriveSpotifyPlaylistUrlFromId(playlistId)
  
  # get playlist data from spotify
  freshPlaylistSpotifyData = UtilsSpotify.fetchSpotifyPlaylistMetadata(spotifyPlaylistId=playlistId)
  if not freshPlaylistSpotifyData:
    message = f"Playlist {playlistId} not found in Spotify. Maybe you made the playlist private or deleted it from Spotify?"
    logger.error(message)
    raise PlaylistAddOne_ResponseError404(message=message).toHttpException()
  
  # create new raw data (for user config)
  addedResult = userConfigReaderApi.addPlaylist(
    add_payload=PlaylistRaw(
      spotify_id=playlistId,
      spotify_url=playlistUrl,
      name=freshPlaylistSpotifyData.name,
      enabled=True,
      lastSpotifyFetchDateTimeISO=None
    )
  )
  
  if addedResult[0] == False:
    message = f"Error adding playlist {playlistId} to user config: {addedResult[1]}"
    logger.error(message)
    raise PlaylistAddOne_ResponseError500(message=message).toHttpException()
  
  return True

@router.post("/{playlist_id}/spotify/refetch", 
             operation_id="playlistSpotifyRefetchPlaylist", 
             summary="Refetch playlist Spotify side",
             description="Refetch playlist Spotify side and save to user config",
             responses={
              404: { "model": PlaylistSpotifyRefetchPlaylist_ResponseError404 },
             },
             )
async def playlist_spotify_refetchPlaylist(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistSpotifyRefetchPlaylist_Response200:
  logger.info(f"Refreshing playlist {playlist_id}")
  
  # 1. ensure playlist exists in user config
  oldPlaylistRaw = userConfigReaderApi.getPlaylistRaw(
    playlist_id=playlist_id,
  )
  if not oldPlaylistRaw:
    message = f"Playlist {playlist_id} not found in your config"
    logger.error(message)
    raise PlaylistSpotifyRefetchPlaylist_ResponseError404(message=message).toHttpException()
  
  # 2. fetch updated playlist data from Spotify
  freshPlaylistSpotifyData = UtilsSpotify.fetchSpotifyPlaylistTracksAndData(
    spotifyPlaylistId=playlist_id
  )
  if not freshPlaylistSpotifyData:
    message = f"Playlist {playlist_id} not found in Spotify, but is in your config. Maybe you made the playlist private or deleted it from Spotify?"
    logger.error(message)
    raise PlaylistSpotifyRefetchPlaylist_ResponseError404(message=message).toHttpException()
    
  freshSpotifyPlaylistTracks = freshPlaylistSpotifyData[1]
  # print(freshSpotifyPlaylistMeta)
  # print(freshSpotifyPlaylistTracks[0])
  
  # 3. derive PlaylistDerived
  oldPlaylistDerived = await DataLayerMapper.mapPlaylistRawToPlaylistDerived_ASYNC(
    userConfigApi=userConfigApi,
    playlistRaw=oldPlaylistRaw,
  )
  
  # 4. create new TrackRaw data (for saving to user config) 
  newConfigTracks: list[TrackRaw] = []
  for freshSpotifyTrack in freshSpotifyPlaylistTracks:  
    # get exiing track for this id    
    oldTrackInConfigData = userConfigReaderApi.getTrackRaw(
      playlist_id=playlist_id, 
      track_id=freshSpotifyTrack.spotify_id, 
    )
    oldTrackInConfig = oldTrackInConfigData[0] if oldTrackInConfigData else None
    # create a nww TrackRaw item
    newConfigTrack = TrackRaw(
      spotify_id=freshSpotifyTrack.spotify_id,
      title=freshSpotifyTrack.title,
      artists=freshSpotifyTrack.artists,
      album=freshSpotifyTrack.album or "",
      release_date=freshSpotifyTrack.release_date or "",
      duration_ms=freshSpotifyTrack.duration_ms or 0,
      preview_url=freshSpotifyTrack.preview_url or "",
      youtube_url=oldTrackInConfig.youtube_url if oldTrackInConfig else None,
      cover_url=freshSpotifyTrack.cover_url,
      recording_label=freshSpotifyTrack.recording_label,
    )
    newConfigTracks.append(newConfigTrack)
    # logger.info(f"newConfigTrack: {newConfigTrack}")
  
  # 5. update/save tracks to user config
  # logger.info(f"json: {newConfigTracks}")
  userConfigReaderApi.updatePlaylistTracks(
    playlist_id=playlist_id,
    newTracksRaw=newConfigTracks,
  )
  userConfigReaderApi.updatePlaylist(
    update_payload=PlaylistRaw(
      spotify_id=oldPlaylistRaw.spotify_id,
      spotify_url=oldPlaylistRaw.spotify_url,
      name=oldPlaylistRaw.name,
      enabled=oldPlaylistRaw.enabled,
      lastSpotifyFetchDateTimeISO=UtilsTime.getCurrentDateTimeIso(),
    )
  )
  
  # 6. derive changes
  oldTracksIds = set([track.spotify_id for track in oldPlaylistDerived.tracks])
  newTracksIds = set([track.spotify_id for track in newConfigTracks])
  addedTracksIds = newTracksIds - oldTracksIds
  deletedTracksIds = oldTracksIds - newTracksIds
  
  # 7. notify new tracks
  playlistName = oldPlaylistDerived.name
  oldTracksCount = len(oldTracksIds)
  newTracksCount = len(newTracksIds)
  addedTracksCount = len(addedTracksIds)
  deletedTracksCount = len(deletedTracksIds)
  await webSocketEventEmitter.emit(
    eventPayload=WsBackendEventPayloadTypeMessage(
      text=f"Playlist \"{playlistName}\" updated!\nTrack count: {oldTracksCount} -> {newTracksCount}.\nAdded tracks: {addedTracksCount}\nDeleted tracks: {deletedTracksCount}",
      severity="SUCCESS"
    )
  )
  
  # 8. reply to client
  return True

@router.post("/edit-track", 
             operation_id="playlistEditTrack", 
             summary="Edit playlist track",
             description="Edit playlist track in user config (youtube url, ...)",
             responses={
               404: { "model": PlaylistEditTrack_ResponseError404 },
             },
             )
async def playlist_editTrack(request: PlaylistEditTrack_RequestBody) -> PlaylistEditTrack_Response200:
  logger.info(f"Editing track {request.track_id} of playlist {request.playlist_id}, request: {request}")
  
  # update
  result = userConfigReaderApi.updatePlaylistTrack(
    update_payload=request
  )
  
  # if track not found, 404
  if result == None or result != True:
    message = f"Track {request.track_id} not found in playlist {request.playlist_id}"
    logger.error(message)
    raise PlaylistEditTrack_ResponseError404(message=message).toHttpException()
  
  return True
    
@router.post("/{playlist_id}/track/{track_id}/youtube/auto-search-url", 
             operation_id="playlistYoutubeAutoSearchUrlSingleTrack", 
             summary="Auto-Search YouTube URL for a track",
             description="Auto find-and-set YouTube URL for a playlist track, using track name and artist as search query",
             responses={
               404: { "model": PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError404 },
               500: { "model": PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500 },
             },
             )
async def playlist_youtube_autoSearchUrl_singleTrack(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistYoutubeAutoSearchUrlSingleTrack_Response200:
  logger.info(f"Find YouTube URL for track {track_id}")
  
  # get track
  trackRawData = userConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
  )
  if not trackRawData:
    message = f"Track {track_id} not found in playlist {playlist_id}"
    logger.error(message)
    raise PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError404(message=message).toHttpException()
  
  # derive track derived
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    userConfigApi=userConfigApi,
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
  )
  
  # find YouTube URL
  youtubeUrl = UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack(trackDerived=trackDerived)
  logger.info(f"Found YouTube URL: {youtubeUrl}")
  if not youtubeUrl:
    message = f"Could not find YouTube URL for track {track_id}"
    logger.error(message)
    raise PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500(message=message).toHttpException()
  
  # update track in config
  updateResult = userConfigReaderApi.updatePlaylistTrack(
    update_payload=PlaylistEditTrackPayload(
      playlist_id=playlist_id,
      track_id=track_id,
      youtube_url=youtubeUrl
    )
  )
  if updateResult != True:
    message = f"Could not update Track {track_id} in playlist {playlist_id}"
    logger.error(message)
    raise PlaylistYoutubeAutoSearchUrlSingleTrack_ResponseError500(message=message).toHttpException()
  
  return updateResult

@router.post("/{playlist_id}/youtube/auto-search-url", 
             operation_id="playlistYoutubeAutoSearchUrlAllTracks", 
             summary="Auto-Search YouTube URL for all tracks (Async Job)",
             description="Auto find-and-set YouTube URL for all playlist tracks that have no YouTube URL",
             responses={
               404: { "model": PlaylistYoutubeAutoSearchUrlAllTracks_ResponseError404 },
             },
             )
async def playlist_youtube_autoSearchUrl_allTracks(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistYoutubeAutoSearchUrlAllTracks_Response200:
  logger.info(f"Find YouTube URL for all tracks of playlist {playlist_id}")
  
  # get playlist
  playlistRaw = userConfigReaderApi.getPlaylistRaw(
    playlist_id=playlist_id,
  )
  if not playlistRaw:
    message = f"Playlist {playlist_id} not found in user config"
    logger.error(message)
    raise PlaylistYoutubeAutoSearchUrlAllTracks_ResponseError404(message=message).toHttpException()
  
  # derive playlist derived
  playlistDerived = await DataLayerMapper.mapPlaylistRawToPlaylistDerived_ASYNC(
    userConfigApi=userConfigApi,
    playlistRaw=playlistRaw,
  )
  
  # crate job (find YouTube URLs) + schedule
  job = UtilsOperations.doYoutubeAutoSarchUrlOnAllPlaylistTracks(playlistDerived)
  await jobQueue.queueJob(job)
  
  return True

@router.get("/{playlist_id}/track/{track_id}/disk/get-audio-file", 
            operation_id="playlistDiskGetAudioFile", 
            summary="Get Audio File of track",
            description="Return Playlist track disk file (downloaded) as Binary File. Use this to play the track in <audio src> tag",
            responses={
              404: { "model": PlaylistDiskGetAudioFile_ResponseError404 },
            }
            )
async def playlist_disk_getAudioFile(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistDiskGetAudioFile_Response200:
  logger.info(f"Play request for track {track_id}")
  
  # get track raw
  trackRawData = userConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
  )
  if not trackRawData:
    message = f"Track {track_id} not found in playlist {playlist_id}"
    logger.error(message)
    raise PlaylistDiskGetAudioFile_ResponseError404(message=message).toHttpException()
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  
  # derive track derived
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    userConfigApi=userConfigApi,
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
  )
  
  # return file
  return FileResponse(
    path=trackDerived.disk_file_path,
    media_type="audio/mpeg",
    filename="song.mp3",
  )
    
@router.post("/{playlist_id}/track/{track_id}/disk/download", 
             operation_id="playlistDiskDownloadSingleTrack", 
             summary="Download (YouTube -> MP3) for a track",
             description="Download single playlist track from YouTube as MP3 and save to disk",
             responses={
               404: { "model": PlaylistDiskDownloadSingleTrack_ResponseError404 },
               500: { "model": PlaylistDiskDownloadSingleTrack_ResponseError500 },
             },
             )
async def playlist_disk_download_singleTrack(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistDiskDownloadSingleTrack_Response200:
  logger.info(f"Downloading track {track_id}")
  
  # get track raw
  trackRawData = userConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
  )
  if not trackRawData:
    message = f"Track {track_id} not found in playlist {playlist_id}"
    logger.error(message)
    raise PlaylistDiskDownloadSingleTrack_ResponseError404(message=message).toHttpException()
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  
  # derive track derived
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    userConfigApi=userConfigApi,
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
  )
  
  # download track
  downloadResult = await UtilsOperations.downloadSingleTrack(trackDerived)
  
  if downloadResult[0] == False and downloadResult[1] == "FFMPEG_NOT_INSTALLED":
    message = "Could not download track because FFMPEG is not installed in your system"
    logger.error(message)
    raise PlaylistDiskDownloadSingleTrack_ResponseError500(message=message).toHttpException()
  
  if downloadResult[0] == False and downloadResult[1] == "NO_YOUTUBE_URL":
    message = "Could not find YouTube URL for track"
    logger.error(message)
    raise PlaylistDiskDownloadSingleTrack_ResponseError500(message=message).toHttpException()
  
  if downloadResult[0] == False and downloadResult[1] == "DISK_PATH_NOT_ACCESSIBLE":
    message = "Could not write to disk folder for track. The directory is not accessible!"
    logger.error(message)
    raise PlaylistDiskDownloadSingleTrack_ResponseError500(message=message).toHttpException()
  
  if downloadResult[0] == False and downloadResult[1] == "ERROR_DOWNLOADING":
    message = f"Could not download track - {downloadResult[2]} - {downloadResult[1]}"
    logger.error(message)
    raise PlaylistDiskDownloadSingleTrack_ResponseError500(message=message).toHttpException()
  
  if downloadResult[0] != True:
    message = f"Could not download track - UNKNOWN_ERROR"
    logger.error(message)
    raise PlaylistDiskDownloadSingleTrack_ResponseError500(message=message).toHttpException()
  
  return True
  
@router.post("/{playlist_id}/disk/download-all/job/start", 
             operation_id="playlistDiskDownloadAllTracks", 
             summary="Download (YouTube -> MP3) for all tracks (Async Job)",
             description="Start async job. Download track from YouTube as MP3 and save to disk, for all tracks of the playlist that have YouTube URL and are not downloaded yet",
             responses={
               404: { "model": PlaylistDiskDownloadAllTracks_ResponseError404 },
             },
             )
async def playlist_disk_download_allTracks(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id])
) -> PlaylistDiskDownloadAllTracks_Response200:
  # get playlist raw
  playlistRaw = userConfigReaderApi.getPlaylistRaw(
    playlist_id=playlist_id,
  )
  if not playlistRaw:
    message = f"Playlist {playlist_id} not found"
    logger.error(message)
    raise PlaylistDiskDownloadAllTracks_ResponseError404(message=message).toHttpException()
  
  # derive playlist derived
  playlistDerived = await DataLayerMapper.mapPlaylistRawToPlaylistDerived_ASYNC(
    userConfigApi=userConfigApi,
    playlistRaw=playlistRaw,
  )
  # create job
  job = UtilsOperations.downloadPlaylistAllMissingTrack(
    playlistDerived=playlistDerived
  )
  # schedule job
  await jobQueue.queueJob(job)
  # reply
  return True
  
@router.post("/{playlist_id}/track/{track_id}/disk/delete-file", 
             operation_id="playlistDiskDeleteTrackFile", 
             summary="Delete playlist track file",
             description="Delete playlist track file (downloaded) from disk",
             responses={
               404: { "model": PlaylistDiskDeleteTrackFile_ResponseError404 },
             },
             )
async def playlist_disk_deleteTrackFile(
  playlist_id: str = FastApiPath(description="Spotify playlist ID",examples=[EXAMPLE_PLAYLIST_DERIVED.spotify_id]),
  track_id: str = FastApiPath(description="Spotify track ID",examples=[EXAMPLE_TRACK_DERIVED.spotify_id]),
) -> PlaylistDiskDeleteTrackFile_Response200:
  logger.info(f"Delete request for track {track_id}")
  
  # get track raw
  trackRawData = userConfigReaderApi.getTrackRaw(
    playlist_id=playlist_id,
    track_id=track_id,
  )
  if not trackRawData:
    message = f"Track {track_id} not found in playlist {playlist_id}"
    logger.error(message)
    raise PlaylistDiskDeleteTrackFile_ResponseError404(message=message).toHttpException()
  trackRaw, playlistRaw, trackRawIndex = trackRawData
  
  # derive track derived
  trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
    userConfigApi=userConfigApi,
    trackRaw=trackRaw,
    playlistRaw=playlistRaw,
    index=trackRawIndex,
  )
  
  # delete file
  deletedResult = UtilsTrackDisk.deleteTrackFile(trackDerived)
  
  if deletedResult == "FILE_NOT_FOUND":
    message = f"Track {track_id} file not found in disk"
    logger.error(message)
    raise PlaylistDiskDeleteTrackFile_ResponseError404(message=message).toHttpException()
  
  if deletedResult == "FILE_DELETE_ERROR":
    message = f"Error deleting track {track_id} file from disk"
    logger.error(message)
    raise PlaylistDiskDeleteTrackFile_ResponseError500(message=message).toHttpException()
  
  return True
  