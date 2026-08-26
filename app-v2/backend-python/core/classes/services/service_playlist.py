import asyncio

from models.playlist import (
  PlaylistRaw, 
  PlaylistDerived,
  TrackRaw,
  TrackDerived,
  PlaylistAddPlaylistPayload, 
  PlaylistEditPlaylistPayload, 
  PlaylistEditTrackPayload,
)
from models.ws import (
  WsBackendEventPayloadTypeMessage,
  WsBackendEventPayloadTypeFrontendQueryInvalidation,
  FrontendQueryKeys,
)

from core.classes.logger.logger import Logger
from core.classes.config.app_config import AppConfig
from core.classes.jobs.job_queue_sequential import JobQueueSequential
from core.classes.jobs.job import Job
from core.classes.data.user_config_api import UserConfigApi
from core.classes.data.data_layer_mapper import DataLayerMapper
from core.classes.data.db import Db
from core.classes.notifications.websocket_event_emitter import WebSocketEventEmitter
from core.classes.utils.utils_native_deps_checker import UtilsNativeDepsChecker
from core.classes.utils.utils_disk import UtilsDisk
from core.classes.utils.utils_time import UtilsTime, UtilsTimeExecutionTimer
from core.classes.music_providers.utils_spotify import UtilsSpotify
from core.classes.music_providers.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi
from core.classes.music_providers.utils_metadata_writer import write_metadata_to_file

class ServicePlaylist:
  def __init__(
    self, 
    logger: Logger,
    userConfigApi: UserConfigApi,
    db: Db,
    appConfig: AppConfig,
    nativeDepsChecker: UtilsNativeDepsChecker,
    webSocketEventEmitter: WebSocketEventEmitter,
    jobQueue: JobQueueSequential,
  ):
    self.logger: Logger = logger
    self.userConfigApi: UserConfigApi = userConfigApi
    self.db: Db = db
    self.appConfig: AppConfig = appConfig
    self.nativeDepsChecker: UtilsNativeDepsChecker = nativeDepsChecker
    self.webSocketEventEmitter: WebSocketEventEmitter = webSocketEventEmitter
    self.jobQueue: JobQueueSequential = jobQueue
    self.complexOperations: ComplexOperations = ComplexOperations(
      logger=logger,
      servicePlaylist=self,
      userConfigApi=userConfigApi,
      webSocketEventEmitter=webSocketEventEmitter,
    )
  
  def getPlaylistsRaw(self):
    dbResult = self.db.getPlaylistsRaw()
    return dbResult
  
  def getPlaylistRaw(self, playlist_id: str):
    dbResult = self.db.getPlaylistRaw(playlist_id=playlist_id)
    return dbResult
  
  async def getPlaylistDerived(self, playlist_id: str):
    # get PlaylistRaw from db
    dbResult = self.db.getPlaylistRaw(playlist_id=playlist_id)
    if dbResult[0] == False:
      return (False, "DB_READ_ERROR", dbResult[1])
    playlistRaw = dbResult[3]
    
    # derive PlaylistDerived
    playlistDerived = await DataLayerMapper.mapPlaylistRawToPlaylistDerived_ASYNC(
      userConfigApi=self.userConfigApi,
      playlistRaw=playlistRaw, 
    )
    
    # ok
    return (True, "FOUND", playlistDerived)
  
  def getTrackRaw(self, playlist_id: str, track_id: str):
    # get TrackRaw from db
    dbReadResult = self.db.getTrackRaw(playlist_id=playlist_id, track_id=track_id)
    if dbReadResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    trackRawIndex = dbReadResult[2]
    trackRaw = dbReadResult[3]
    
    # ok
    return (True, "FOUND", trackRawIndex, trackRaw)
  
  def getTrackDerived(self, playlist_id: str, track_id: str):
    # get PlaylistRaw from db
    dbReadPlaylistResult = self.db.getPlaylistRaw(playlist_id=playlist_id)
    if dbReadPlaylistResult[0] == False:
      return (False, "PLAYLIST_NOT_FOUND_IN_DB")
    playlistRaw = dbReadPlaylistResult[3]
    
    # get TrackRaw from db
    dbReadResult = self.getTrackRaw(playlist_id=playlist_id, track_id=track_id)
    if dbReadResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    trackRawIndex = dbReadResult[2]
    trackRaw = dbReadResult[3]
    
    # derive TrackDerived
    trackDerived = DataLayerMapper.mapTrackRawToTrackDerived(
      trackRaw=trackRaw,
      index=trackRawIndex,
      playlistRaw=playlistRaw,
      userConfigApi=self.userConfigApi,
    )
    
    # ok
    return (True, "FOUND", trackDerived)
  
  def addPlaylist(self, payload: PlaylistAddPlaylistPayload):
    # derive playlist spotify id
    playlistId = UtilsSpotify.deriveSpotifyPlaylistIdFromUrl(spotifyPlaylistUrl=payload.playlistSpotifyUrl)
    playlistUrl = UtilsSpotify.deriveSpotifyPlaylistUrlFromId(spotifyPlaylistId=playlistId)
    
    # get playlist data from spotify
    freshPlaylistSpotifyData = UtilsSpotify.fetchSpotifyPlaylistMetadata(spotifyPlaylistId=playlistId)
    if not freshPlaylistSpotifyData:
      return (False, "SPOTIFY_FETCH_ERROR")
    
    # create new playlist raw object
    newPlaylistRaw = PlaylistRaw(
      spotify_id=playlistId,
      spotify_url=playlistUrl,
      name=freshPlaylistSpotifyData.name,
      enabled=True,
      lastSpotifyFetchDateTimeISO=None
    )
    
    # add to db
    dbAddResult = self.db.addPlaylistRaw(add_payload=newPlaylistRaw)
    if dbAddResult[0] == False:
      return (False, "DB_ADD_ERROR", dbAddResult[1])
    
    # ok
    return (True, "ADDED")
  
  def updatePlaylist(self, payload: PlaylistEditPlaylistPayload):
    # get old PlaylistRaw from db
    dbReadResult = self.db.getPlaylistRaw(playlist_id=payload.playlist_id)
    if dbReadResult[0] == False:
      return (False, "DB_READ_ERROR", dbReadResult[1])
    oldPlaylistRaw = dbReadResult[3]
    
    # create clone of PlaylistRaw
    newPlaylistRaw = oldPlaylistRaw.model_copy(deep=True)
    
    # if payload has "directory_name" field, update disk
    if payload.directory_name:
      oldDirName = oldPlaylistRaw.directory_name or oldPlaylistRaw.name
      newDirName = payload.directory_name
      oldPath = self.userConfigApi.config_as_object.setting_disk_download_path + "/" + oldDirName
      newPath = self.userConfigApi.config_as_object.setting_disk_download_path + "/" + newDirName
      oldExists = UtilsDisk.checkIfFileExists(oldPath)
      if not oldExists:
        newPlaylistRaw.directory_name = newDirName
      else:
        diskMoveResult = UtilsDisk.moveFileOrDirectory(oldPath=oldPath,newPath=newPath)
        if diskMoveResult:
          newPlaylistRaw.directory_name = newDirName
    
    # save back to db
    dbUpdateResult = self.db.updatePlaylistRawData(
      playlist_id=payload.playlist_id,
      updatedPlaylistRaw=newPlaylistRaw,
    )
    
    # ok
    return dbUpdateResult
  
  def updatePlaylistTrack(self, payload: PlaylistEditTrackPayload):
    # get TrackRaw from db
    oldTrackRawResult = self.getTrackRaw(playlist_id=payload.playlist_id, track_id=payload.track_id)
    if oldTrackRawResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    oldTrackRaw = oldTrackRawResult[3]
    
    # create clone of TrackRaw
    newTrackRaw = oldTrackRaw.model_copy(deep=True)
    
    # mutate
    if payload.youtube_url is None:
      newTrackRaw.youtube_url = None
    elif payload.youtube_url:
      newTrackRaw.youtube_url = payload.youtube_url
    
    # save back to db
    dbUpdateResult = self.db.updateTrackRawData(
      playlist_id=payload.playlist_id,
      updatedTrackRaw=newTrackRaw,
    )
    if dbUpdateResult[0] == False:
      return (False, "DB_UPDATE_TRACK_ERROR", dbUpdateResult[1])
    
    # ok
    return (True, "UPDATED")
  
  async def spotify_refetchPlaylist_then_updatePlaylist(self, playlist_id: str):
    # ensure PlaylistRaw exists in db
    dbReadResult = self.db.getPlaylistRaw(playlist_id=playlist_id)
    if dbReadResult[0] == False:
      return (False, "PLAYLIST_NOT_FOUND_IN_DB")
    oldPlaylistRaw = dbReadResult[3]
    
    # derive PlaylistDerived
    oldPlaylistDerived = await DataLayerMapper.mapPlaylistRawToPlaylistDerived_ASYNC(
      userConfigApi=self.userConfigApi,
      playlistRaw=oldPlaylistRaw,
    )
    
    # get fresh spotify data
    freshPlaylistSpotifyData = UtilsSpotify.fetchSpotifyPlaylistTracksAndData(spotifyPlaylistId=playlist_id)
    if not freshPlaylistSpotifyData:
      return (False, "SPOTIFY_FETCH_ERROR")
    freshPlaylistInfo = freshPlaylistSpotifyData[0]
    freshSpotifyPlaylistTracks = freshPlaylistSpotifyData[1]
    
    # debug
    # print(f"Spotify playlist info: {freshPlaylistInfo}")
    
    # create new TrackRaw list
    newTracksRaw: list[TrackRaw] = []
    for freshSpotifyTrack in freshSpotifyPlaylistTracks:  
      freshId = freshSpotifyTrack.spotify_id
      # get track for this id if exists
      oldTrackDerived = next(
        (
          track
          for track in oldPlaylistDerived.tracks
          if track.spotify_id == freshId
        ),
        None
      )
      # create a new TrackRaw item
      newConfigTrack = TrackRaw(
        spotify_id=freshSpotifyTrack.spotify_id,
        title=freshSpotifyTrack.title,
        artists=freshSpotifyTrack.artists,
        album=freshSpotifyTrack.album or "",
        release_date=freshSpotifyTrack.release_date or "",
        duration_ms=freshSpotifyTrack.duration_ms or 0,
        preview_url=freshSpotifyTrack.preview_url or "",
        youtube_url=oldTrackDerived.youtube_url if oldTrackDerived else None,
        cover_url=freshSpotifyTrack.cover_url,
        recording_label=freshSpotifyTrack.recording_label,
      )
      newTracksRaw.append(newConfigTrack)
    
    # update tracks in db
    dbUpdateTracksResult = self.db.updatePlaylistTracksRaw(playlist_id=playlist_id, updatedTracksRaw=newTracksRaw)
    if dbUpdateTracksResult[0] == False:
      return (False, "DB_UPDATE_TRACKS_ERROR", dbUpdateTracksResult[1])
    
    # update playlist data in db
    newPlaylistRaw = PlaylistRaw(
      # update lastSpotifyFetchDateTimeISO to now
      lastSpotifyFetchDateTimeISO=UtilsTime.getCurrentDateTimeIso(),
      # keep these from old
      spotify_id=oldPlaylistRaw.spotify_id,
      spotify_url=oldPlaylistRaw.spotify_url,
      enabled=oldPlaylistRaw.enabled,
      # update name with fresh
      name=freshPlaylistInfo.name,
      # use prev directory name if exists or fallback to playlist name
      directory_name=oldPlaylistRaw.directory_name or oldPlaylistRaw.name,
    )
    dbUpdatePlaylistResult = self.db.updatePlaylistRawData(playlist_id=playlist_id, updatedPlaylistRaw=newPlaylistRaw)
    if dbUpdatePlaylistResult[0] == False:
      return (False, "DB_UPDATE_PLAYLIST_ERROR", dbUpdatePlaylistResult[1])
    
    # prepare summary of changes
    oldTracksIds = set([track.spotify_id for track in oldPlaylistDerived.tracks])
    newTracksIds = set([track.spotify_id for track in newTracksRaw])
    addedTracksIds = newTracksIds - oldTracksIds
    deletedTracksIds = oldTracksIds - newTracksIds
    playlistName = oldPlaylistDerived.name
    oldTracksCount = len(oldTracksIds)
    newTracksCount = len(newTracksIds)
    addedTracksCount = len(addedTracksIds)
    deletedTracksCount = len(deletedTracksIds)
    
    # notify frontend
    await self.webSocketEventEmitter.emit(
      eventPayload=WsBackendEventPayloadTypeMessage(
        text=f"Playlist \"{playlistName}\" updated!\nTrack count: {oldTracksCount} -> {newTracksCount}.\nAdded tracks: {addedTracksCount}\nDeleted tracks: {deletedTracksCount}",
        severity="SUCCESS"
      )
    )
    
    # ok
    return (True, "UPDATED")
  
  def youtube_autoSearchUrlSingleTrack_then_updateTrack(self, playlist_id: str, track_id: str):
    # get TrackDerived from db
    dbReadResult = self.getTrackDerived(playlist_id=playlist_id, track_id=track_id)
    if dbReadResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    oldTrackDerived = dbReadResult[2]
    
    # find YouTube URL
    youtubeUrl = UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack(trackDerived=oldTrackDerived)
    if not youtubeUrl:
      return (False, "YOUTUBE_URL_NOT_FOUND")
    
    # update TrackRaw
    dbUpdateResult = self.updatePlaylistTrack(
      payload=PlaylistEditTrackPayload(
        playlist_id=playlist_id,
        track_id=track_id,
        youtube_url=youtubeUrl,
      )
    )
    if dbUpdateResult[0] == False:
      return (False, "DB_UPDATE_TRACK_ERROR", dbUpdateResult[1])
    
    # ok
    return (True, "UPDATED")
  
  async def youtube_autoSearchUrlAllTracks_scheduleJob(self, playlist_id: str):
    # get PlaylistDerived from db
    playlistDerivedResult = await self.getPlaylistDerived(playlist_id=playlist_id)
    if playlistDerivedResult[0] == False:
      return (False, "PLAYLIST_NOT_FOUND_IN_DB")
    playlistDerived = playlistDerivedResult[2]
    
    # create job (find YouTube URLs) + schedule
    job = self.complexOperations.doYoutubeAutoSarchUrlOnAllPlaylistTracks(playlistDerived=playlistDerived)
    await self.jobQueue.queueJob(job=job)
    
    # ok
    return (True, "JOB_SCHEDULED")
  
  def disk_getTrackFileAsBinary(self, playlist_id: str, track_id: str):
    # get track raw
    trackDerivedResult = self.getTrackDerived(playlist_id=playlist_id, track_id=track_id)
    if trackDerivedResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    trackDerived = trackDerivedResult[2]
    
    # ensure file exists
    filePath = trackDerived.disk_file_path
    fileExists = UtilsDisk.checkIfFileExists(filePath=trackDerived.disk_file_path)
    if not fileExists:
      return (False, "FILE_NOT_FOUND_ON_DISK")
    
    # ok
    return (True, "FOUND", filePath)
  
  async def disk_downloadSingleTrack(self, playlist_id: str, track_id: str):
    # get TrackDerived from db
    trackDerivedResult = self.getTrackDerived(playlist_id=playlist_id, track_id=track_id)
    if trackDerivedResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    trackDerived = trackDerivedResult[2]
    
    # download track
    downloadResult = await self.complexOperations.downloadSingleTrack(trackDerived=trackDerived)
    if downloadResult[0] == False:
      reasonCode = downloadResult[1]
      return (False, "ERROR_DOWNLOADING", reasonCode)
    
    # ok
    return (True, "DOWNLOADED")
  
  async def disk_downloadAllTracks(self, playlist_id: str):
    # get PlaylistDerived from db
    playlistDerivedResult = await self.getPlaylistDerived(playlist_id=playlist_id)
    if playlistDerivedResult[0] == False:
      return (False, "PLAYLIST_NOT_FOUND_IN_DB")
    playlistDerived = playlistDerivedResult[2]
    # create job + schedule
    job = self.complexOperations.downloadPlaylistAllMissingTrack(playlistDerived=playlistDerived)
    await self.jobQueue.queueJob(job)
    # ok
    return (True, "JOB_SCHEDULED")
  
  def disk_deleteTrackFile(self, playlist_id: str, track_id: str):
    # get TrackDerived from db
    trackDerivedResult = self.getTrackDerived(playlist_id=playlist_id, track_id=track_id)
    if trackDerivedResult[0] == False:
      return (False, "TRACK_NOT_FOUND_IN_DB")
    trackDerived = trackDerivedResult[2]
    
    # delete file
    filePath = trackDerived.disk_file_path
    deletedResult = UtilsDisk.deleteFile(filePath=filePath)
    if deletedResult == "SUCCESS":
      return (True, "DELETED")
    
    # fail
    return (False, deletedResult)
  
  
class ComplexOperations:
  """Complex Operations of ServicePlaylist"""
  def __init__(
    self,
    servicePlaylist: ServicePlaylist,
    logger: Logger,
    userConfigApi: UserConfigApi,
    webSocketEventEmitter: WebSocketEventEmitter,
  ):
    self.servicePlaylist: ServicePlaylist = servicePlaylist
    self.logger: Logger = logger
    self.userConfigApi: UserConfigApi = userConfigApi
    self.webSocketEventEmitter: WebSocketEventEmitter = webSocketEventEmitter
  
  async def downloadSingleTrack(self, trackDerived: TrackDerived):
    """Download single track and optionally embed metadata."""
    
    # sub-fns
    async def downloadFile(trackDerived: TrackDerived):
      maxRetries = 5
      retryCount = 0
      execTimer = UtilsTimeExecutionTimer()
      errorCodes: list[str] = []
      while (retryCount < maxRetries):
        retryCount += 1
        # download
        output = await asyncio.to_thread(
          UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3,
          trackDerived=trackDerived
        )
        # if success -> return
        if output[0]:
          executionTime = execTimer.end()
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Attempt {retryCount}/{maxRetries} to download track. Success! Duration: {executionTime}")
          )
          return output
        # if failed -> retry
        errorCodes.append(output[1])
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Attempt {retryCount}/{maxRetries} to download track. Failed {output[1]}. Retrying...")
        )
      # if failed after max retries
      executionTime = execTimer.end()
      await self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(text=f"Failed to download track after {maxRetries} attempts. Duration: {executionTime}")
      )
      return (False, "MAX_RETRIES_EXCEEDED", errorCodes)
    
    async def addMetadataToFile(trackDerived: TrackDerived):
      maxRetries = 5
      retryCount = 0
      execTimer = UtilsTimeExecutionTimer()
      while (retryCount < maxRetries):
        retryCount += 1
        # embed
        output = await write_metadata_to_file(
          file_path=trackDerived.disk_file_path,
          track_data=trackDerived,
        )
        # if success -> return
        if output[0]:
          executionTime = execTimer.end()
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Attempt {retryCount}/{maxRetries} to embed metadata. Success! Duration: {executionTime}")
          )
          return output
        # if failed -> retry
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Attempt {retryCount}/{maxRetries} to embed metadata. Failed. {output[1]}. Retrying...")
        )
      # if failed after max retries
      executionTime = execTimer.end()
      await self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(text=f"Failed to embed metadata after {maxRetries} attempts. Duration: {executionTime}")
      )
      return (False, "MAX_RETRIES_EXCEEDED")
    
    # 1. sleep
    await asyncio.sleep(2)

    # 2. Download track with retry
    self.logger.info(f"Downloading track {trackDerived.artists} - {trackDerived.title}")
    downloadResult = await downloadFile(trackDerived=trackDerived)
    if downloadResult[0] == False:
      errorCode = downloadResult[1]
      errorReason = len(downloadResult) > 2 and downloadResult[2] or None
      self.logger.warning(f"Downloading track {trackDerived.artists} - {trackDerived.title} ❌ FAILED: {errorCode} - {errorReason or ''}")
      return downloadResult

    # 3. Embed metadata if enabled
    if self.userConfigApi.config_as_object.setting_disk_add_meta_tags:
      self.logger.info(f"Embedding metadata for track {trackDerived.artists} - {trackDerived.title}")
      metadata_result = await addMetadataToFile(trackDerived=trackDerived)
      if metadata_result[0] == False:
        self.logger.warning(f"Embedding metadata for track {trackDerived.artists} - {trackDerived.title} ❌ FAILED: {metadata_result[1]}")
        return metadata_result

    return (True, "SUCCESS")
  
  def downloadPlaylistAllMissingTrack(self, playlistDerived: PlaylistDerived):
    # define job input
    playlistId = playlistDerived.spotify_id
    tracksDerived = playlistDerived.model_copy(deep=True).tracks
    trackCount = len(tracksDerived)
    jobStepCount = trackCount
    
    # crate job fn
    async def jobFn(job: Job):
      # constants
      delayBetweenTracks = 0.05
      
      # for each track
      for trackIndex, track in enumerate(tracksDerived):
        trackNum = trackIndex + 1
        trackNumLogMsg = f"Track {trackNum}/{trackCount}"
        
        await asyncio.sleep(delayBetweenTracks)
        
        # if not must be downloaded -> skip
        hasYoutubeUrl = bool(track.youtube_url)
        hasDiskFile = bool(track.has_disk_file)
        if hasYoutubeUrl and hasDiskFile:
          await job.incrementStepCompleted()
          await job.captureMessage(
            kind="INFO",
            message=f"{trackNumLogMsg} - Skip (already downloaded)"
          )
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"{trackNumLogMsg} - Skip (already downloaded)")
          )
          continue
        
        if not hasYoutubeUrl:
          await job.incrementStepCompleted()
          await job.captureMessage(
            kind="INFO",
            message=f"{trackNumLogMsg} - Skip (no YouTube URL)"
          )
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"{trackNumLogMsg} - Skip (no YouTube URL)")
          )
          continue
        
        # if must be downloaded -> download
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"{trackNumLogMsg} - Downloading...")
        )
        downloadResult = await self.downloadSingleTrack(trackDerived=track)
        
        # - if error -> signal error but continue job
        if (not downloadResult[0]):
          await job.captureMessage(
            kind="ERROR",
            message=f"{trackNumLogMsg} - Downloading ❌ FAILED: {downloadResult[1]}"
          )
        # - if success -> notify frontend
        else:
          await job.captureMessage(
            kind="INFO",
            message=f"{trackNumLogMsg} - Downloading ✅ SUCCESS"
          )
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"{trackNumLogMsg} - Downloading ✅ SUCCESS")
          )
          
        # mark step as done
        await job.incrementStepCompleted()
        
        # notify frontend to invalidate playlist details
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeFrontendQueryInvalidation(
            queryKeys=FrontendQueryKeys.PLAYLIST_DETAILS(playlistId)
          )
        )
        
      # after all track handled -> notify frontend to invalidate playlist details
      await self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeFrontendQueryInvalidation(
          queryKeys=FrontendQueryKeys.PLAYLIST_DETAILS(playlistId)
        )
      )

    # create job
    job = Job(
      title=f"Download Playlist: {playlistDerived.name}",
      totalStepCount=jobStepCount,
      jobFn=jobFn
    )
    return job
  
  def doYoutubeAutoSarchUrlOnAllPlaylistTracks(self, playlistDerived: PlaylistDerived):
    
    # 1. get data
    playlistId = playlistDerived.spotify_id
    tracksCount = len(playlistDerived.tracks)
    
    # sub-fns
    async def findYoutubeUrlOfTrack(trackDerived: TrackDerived):
      maxRetries = 5
      retryCount = 0
      while (retryCount < maxRetries):
        retryCount += 1
        output = await asyncio.to_thread(
          UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack,
          trackDerived=trackDerived
        )
        if output:
          return output
      return None
    
    # 2. define job fn
    async def jobFn(job: Job):
      for trackIndex, track in enumerate(playlistDerived.tracks):
        
        # 1. get status
        mustBeFetched = not track.youtube_url
        
        # - if youtube is already set -> skip
        if not mustBeFetched:
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Skip (YouTube URL exists)")
          )
          await job.incrementStepCompleted()
          continue
        
        # 2. fetch
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching Youtube URL...")
        )
        # - find YouTube URL
        youtubeUrl = await findYoutubeUrlOfTrack(trackDerived=track)
        # - if not found -> go next
        if not youtubeUrl:
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching YouTube URL ❌ FAILED")
          )
          await job.incrementStepCompleted()
          continue
        
        # 3. update track in config
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching YouTube URL ✅ SUCCESS")
        )
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL...")
        )
        updateResult =self.servicePlaylist.updatePlaylistTrack(
          payload=PlaylistEditTrackPayload(
            playlist_id=playlistDerived.spotify_id,
            track_id=track.spotify_id,
            youtube_url=youtubeUrl
          )
        )
        # - if update failed
        if updateResult[0] == False:
          await self.webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL ❌ FAILED")
          )
          await job.incrementStepCompleted()
          continue
        
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL ✅ SUCCESS")
        )
            
        # 4. mark step as completed
        await job.incrementStepCompleted()
        
        # 5. notify frontend to invalidate playlist details
        await self.webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeFrontendQueryInvalidation(
            queryKeys=FrontendQueryKeys.PLAYLIST_DETAILS(playlistId)
          )
        )
    
    # 3. create job
    job = Job(
      title="Find YouTube URL for all tracks of playlist",
      totalStepCount=tracksCount,
      jobFn=jobFn
    )
    
    return job