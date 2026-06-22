import asyncio
from models.new import (
  PlaylistDerived, 
  TrackDerived,
  PlaylistEditTrackPayload, 
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
    # sleep
    await asyncio.sleep(2)

    # Download track
    download_result = await asyncio.to_thread(
      UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3,
      trackDerived=trackDerived
    )

    if not download_result[0]:
      return download_result

    # Embed metadata if enabled
    if userConfigApi.config_as_object.setting_disk_add_meta_tags:
      metadata_result = await write_metadata_to_file(
        file_path=trackDerived.disk_file_path,
        track_data=trackDerived,
        add_meta_tags=True
      )
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
        # if error -> fail the job
        if (not downloadResult[0]):
          job.raiseError(downloadResult[1])
          return
        
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
    
    # get data
    playlistId = playlistDerived.spotify_id
    tracksCount = len(playlistDerived.tracks)
    
    # define job fn
    async def jobFn(job: Job):
      for trackIndex, track in enumerate(playlistDerived.tracks):
        
        # get status
        mustBeFetched = not track.youtube_url
        
        # if youtube is already set -> skip
        if not mustBeFetched:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Skip (YouTube URL exists)")
          )
          await job.incrementStepCompleted()
          continue
        
        # if not already fetched -> fetch
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching Youtube URL...")
        )
        
        # find YouTube URL
        youtubeUrl = UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack(trackDerived=track)
        
        # if not found -> go next
        if not youtubeUrl:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Searching YouTube URL ❌ FAILED")
          )
          await job.incrementStepCompleted()
          continue
        
        # if found -> update track in config
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
        
        # if update failed
        if not updateResult:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL ❌ FAILED")
          )
          await job.incrementStepCompleted()
          continue
        
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Track {trackIndex+1}/{tracksCount} - Updating YouTube URL ✅ SUCCESS")
        )
            
        # mark step as completed
        await job.incrementStepCompleted()
        
        # notify frontend to invalidate playlist details
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeFrontendQueryInvalidation(
            queryKeys=FrontendQueryKeys.PLAYLIST_DETAILS(playlistId)
          )
        )
    
    # create job
    job = Job(
      title="Find YouTube URL for all tracks of playlist",
      totalStepCount=tracksCount,
      jobFn=jobFn
    )
    
    return job