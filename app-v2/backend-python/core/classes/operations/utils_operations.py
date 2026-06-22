import asyncio
from models.new import (
  PlaylistDerived, 
  TrackDerived,
  PlaylistEditTrackPayload, 
  WsBackendEventPayload,
  WsBackendEventPayloadTypeMessage,
  WsBackendEventPayloadTypeFrontendQueryInvalidation,
  FrontendQueryKeys
)
from core.singleton.logger import logger
from core.singleton.user_config_api import userConfigApi, userConfigReaderApi
from core.singleton.websocket_event_emitter import webSocketEventEmitter
from core.classes.jobs.job import Job
from core.classes.music_providers.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi
from core.classes.music_providers.utils_metadata_writer import write_metadata_to_file


class UtilsOperations:
  """High Level API for playlist and tracks operations"""
  @staticmethod
  async def downloadSingleTrack(trackDerived: TrackDerived):
    """Download single track and optionally embed metadata."""
    
    # sub-fns
    async def downloadFile(trackDerived: TrackDerived):
      maxRetries = 5
      retryCount = 0
      while (retryCount < maxRetries):
        retryCount += 1
        output = await asyncio.to_thread(
          UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3,
          trackDerived=trackDerived
        )
        if output[0]:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Attempt {retryCount}/{maxRetries} to download track. Success!")
          )
          return output
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Attempt {retryCount}/{maxRetries} to download track. Failed. Retrying...")
        )
      await webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(text=f"Failed to download track after {maxRetries} attempts.")
      )
      return output
    
    async def addMetadataToFile(trackDerived: TrackDerived):
      maxRetries = 5
      retryCount = 0
      while (retryCount < maxRetries):
        retryCount += 1
        output = await write_metadata_to_file(
          file_path=trackDerived.disk_file_path,
          track_data=trackDerived,
          add_meta_tags=True
        )
        if output[0]:
          return output
      return output
    
    # 1. sleep
    await asyncio.sleep(2)

    # 2. Download track with retry
    download_result = await downloadFile(trackDerived=trackDerived)
    if not download_result[0]:
      logger.warning(f"Failed to download track: {download_result[1]}")
      return download_result

    # 3. Embed metadata if enabled
    if userConfigApi.config_as_object.setting_disk_add_meta_tags:
      metadata_result = await addMetadataToFile(trackDerived=trackDerived)
      if not metadata_result[0]:
        logger.warning(f"Failed to embed metadata: {metadata_result[1]}")

    return download_result
  
  @staticmethod
  def downloadPlaylistAllMissingTrack(playlistDerived: PlaylistDerived):
    # define job input
    playlistId = playlistDerived.spotify_id
    tracksDerived = playlistDerived.model_copy(deep=True).tracks
    trackCount = len(tracksDerived)
    jobStepCount = trackCount
    
    # crate job fn
    async def jobFn(job: Job):
      # constants
      delayBetweenTracks = 0.05
      
      # download each track
      for trackIndex, track in enumerate(tracksDerived):
        
        await asyncio.sleep(delayBetweenTracks)
        
        # if not must be downloaded -> skip
        mustBeDownloaded = track.youtube_url and not track.has_disk_file
        if not mustBeDownloaded:
          await job.incrementStepCompleted()
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{trackCount} - Skip (already downloaded)")
          )
          continue
        
        # if must be downloaded -> download
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{trackCount} - Downloading...")
        )
        downloadResult = await UtilsOperations.downloadSingleTrack(trackDerived=track)
        # if error -> retry
        if (not downloadResult[0]):
          job.raiseError(downloadResult[1])
        
        # if success -> notify frontend
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{trackCount} - Downloading ✅ SUCCESS")
        )
          
        # mark step as done
        await job.incrementStepCompleted()
        
        # notify frontend to invalidate playlist details
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeFrontendQueryInvalidation(
            queryKeys=FrontendQueryKeys.PLAYLIST_DETAILS(playlistId)
          )
        )
        
      # after all track handled -> notify frontend to invalidate playlist details
      await webSocketEventEmitter.emit(
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
  
  @staticmethod
  def doYoutubeAutoSarchUrlOnAllPlaylistTracks(playlistDerived: PlaylistDerived):
    
    # sub-fns
    async def findYoutubeUrlOfTrack(trackDerived: TrackDerived):
      maxRetries = 5
      retryCount = 0
      while (retryCount < maxRetries):
        output = await asyncio.to_thread(
          UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack,
          trackDerived=trackDerived
        )
        if output:
          return output
      return None
    
    # 1. get data
    playlistId = playlistDerived.spotify_id
    tracksCount = len(playlistDerived.tracks)
    
    # 2. define job fn
    async def jobFn(job: Job):
      for trackIndex, track in enumerate(playlistDerived.tracks):
        
        # 1. get status
        mustBeFetched = not track.youtube_url
        
        # - if youtube is already set -> skip
        if not mustBeFetched:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Skip (YouTube URL exists)")
          )
          await job.incrementStepCompleted()
          continue
        
        # 2. fetch
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching Youtube URL...")
        )
        # - find YouTube URL
        youtubeUrl = await findYoutubeUrlOfTrack(trackDerived=track)
        # - if not found -> go next
        if not youtubeUrl:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching YouTube URL ❌ FAILED")
          )
          await job.incrementStepCompleted()
          continue
        
        # 3. update track in config
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching YouTube URL ✅ SUCCESS")
        )
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL...")
        )
        updateResult = userConfigReaderApi.update_playlist_track(
          update_payload=PlaylistEditTrackPayload(
            playlist_id=playlistDerived.spotify_id,
            track_id=track.spotify_id,
            youtube_url=youtubeUrl
          )
        )
        # - if update failed
        if not updateResult:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL ❌ FAILED")
          )
          await job.incrementStepCompleted()
          continue
        
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL ✅ SUCCESS")
        )
            
        # 4. mark step as completed
        await job.incrementStepCompleted()
        
        # 5. notify frontend to invalidate playlist details
        await webSocketEventEmitter.emit(
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