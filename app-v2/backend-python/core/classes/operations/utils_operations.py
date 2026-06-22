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
    await asyncio.sleep(1)

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
        
        # check if track must be downloaded
        mustBeDownloaded = track.youtube_url and not track.has_disk_file
        
        # if must be downloaded -> download
        if mustBeDownloaded:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(
              text=f"Downloading track {trackIndex+1}/{trackCount}..."
            )
          )
          # download if required
          downloadResult = await UtilsOperations.downloadSingleTrack(trackDerived=track)
          # if success
          if (downloadResult[0] == True):
            await webSocketEventEmitter.emit(
              eventPayload=WsBackendEventPayloadTypeMessage(
                text=f"Downloaded track {trackIndex+1}/{trackCount}\n With metadata embedded"
              )
            )
          # if error -> fail the job
          else:
            job.raiseError(downloadResult[1])
        # if not must be downloaded -> skip
        else: 
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(
              text=f"Skipped track {trackIndex+1}/{trackCount}"
            )
          )
          
        # mark step as done
        job.incrementStepCompleted()
        
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
      def markStepCompleted():
        job.incrementStepCompleted()
        
      for trackIndex, track in enumerate(playlistDerived.tracks):
        # get status
        mustBeFetched = not track.youtube_url
        
        # if youtube is already set -> skip
        if not mustBeFetched:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Skipping track {trackIndex+1}/{tracksCount}! It already has a YouTube URL")
          )
          markStepCompleted()
          continue
        
        # if not already fetched -> fetch
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Searching YouTube URL for track {trackIndex+1}/{tracksCount}...")
        )
        
        # find YouTube URL
        youtubeUrl = UtilsYoutubeFetcherApi.findYoutubeUrlOfTrack(trackDerived=track)
        
        # if not found -> go next
        if not youtubeUrl:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Failed to find YouTube URL for track {trackIndex+1}/{tracksCount}")
          )
          markStepCompleted()
          continue
        
        # if found -> update track in config
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Found YouTube URL for track {trackIndex+1}/{tracksCount}...")
        )
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Updating YouTube URL for track {trackIndex+1}/{tracksCount}...")
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
            eventPayload=WsBackendEventPayloadTypeMessage(text=f"Failed to update YouTube URL for track {trackIndex+1}/{tracksCount}")
          )
          markStepCompleted()
          continue
        
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(text=f"Updated YouTube URL for track {trackIndex+1}/{tracksCount}")
        )
            
        # mark step as completed
        markStepCompleted()
        
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