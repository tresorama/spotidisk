import asyncio
from models.new import (
  TrackDerived, 
  PlaylistDerived, 
  WsBackendEventPayloadTypeFrontendQueryInvalidation, 
  WsBackendEventPayloadTypeMessage, 
  FrontendQueryKeys
)
from core.singleton.websocket_event_emitter import webSocketEventEmitter
from core.classes.job import Job
from core.classes.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi

class UtilsDownload:
  """High Level Download API for playlist and tracks"""
  @staticmethod
  def downloadSingleTrack(trackDerived: TrackDerived):
    return UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3(trackDerived)
  
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
      delayBetweenTracks = 1
      # download each track
      for trackIndex, track in enumerate(tracksDerived):
        await asyncio.sleep(delayBetweenTracks)
        # check if track must be downloaded
        mustBeDownloaded = track.youtube_url and not track.has_disk_file
        if mustBeDownloaded:
          await webSocketEventEmitter.emit(
            eventPayload=WsBackendEventPayloadTypeMessage(
              text=f"Downloading track {trackIndex+1}/{trackCount}..."
            )
          )
          stepResult = await asyncio.to_thread(
            UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3, 
            trackDerived=track
          )
          if (stepResult[0] == True):
            await webSocketEventEmitter.emit(
              eventPayload=WsBackendEventPayloadTypeMessage(
                text=f"Downloaded track {trackIndex+1}/{trackCount}"
              )
            )
          else: 
            job.raiseError(stepResult[1])
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