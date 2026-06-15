from models.new import TrackDerived, PlaylistDerived
from core.singleton.job_state_memory import jobStateMemory
from core.classes.job_state import JobState
from core.classes.utils_youtube_fetcher_api import UtilsYoutubeFetcherApi

class UtilsDownload:
  """High Level Download API for playlist and tracks"""
  @staticmethod
  def downloadSingleTrack(trackDerived: TrackDerived):
    return UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3(trackDerived)
  
  @staticmethod
  def downloadPlaylistAllMissingTrack(playlistDerived: PlaylistDerived):
    # get job data
    tracksDerived = playlistDerived.model_copy(deep=True).tracks
    tracksCount = len(tracksDerived)
    jobStepCount = tracksCount
    
    # create job fn
    def jobFn():
      jobState = jobStateMemory.getJobState()
      if not jobState:
        raise Exception("No job state found")
      # download
      for trackDerived in tracksDerived:
        mustBeDownloaded = trackDerived.youtube_url and not trackDerived.has_disk_file
        if mustBeDownloaded:
          UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3(trackDerived)
        jobState.incrementStep()
    
    # init job
    jobState = JobState(
      title=f"Playlist Download All Tracks\nPlaylist: {playlistDerived.name}",
      totalStepCount=jobStepCount,
      jobFn=jobFn
    )
    
    # return
    return jobState