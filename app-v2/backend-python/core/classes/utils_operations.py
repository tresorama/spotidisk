from models.new import (
  PlaylistDerived, 
  PlaylistEditTrackPayload, 
  WsBackendEventPayloadTypeMessage,
  WsBackendEventPayloadTypeFrontendQueryInvalidation,
  FrontendQueryKeys
)
from core.singleton.user_config_api import userConfigApi
from core.singleton.websocket_event_emitter import webSocketEventEmitter
from core.classes.job import Job
from core.classes.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi


class UtilsOperations:
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
        updateResult = userConfigApi.update_playlist_track(PlaylistEditTrackPayload(
          playlist_id=playlistDerived.spotify_id,
          track_id=track.spotify_id,
          youtube_url=youtubeUrl
        ))
        
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