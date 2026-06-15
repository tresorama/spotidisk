from models.new import TrackDerived, PlaylistDerived
from core.singleton.jobs_executor import jobsExecutor
from core.classes.job import Job
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
    async def jobFn():
      # ensure this job is not cancelled
      jobData = jobsExecutor.getCurrentJob()
      if not jobData: raise Exception("No job state found")
      job, jobTask = jobData
      if jobTask.cancelled(): raise Exception("Job was cancelled")
      # download
      for trackDerived in tracksDerived:
        mustBeDownloaded = trackDerived.youtube_url and not trackDerived.has_disk_file
        if mustBeDownloaded:
          UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3(trackDerived)
        job.incrementStep()
    
    # init job
    job = Job(
      title=f"Playlist Download All Tracks\nPlaylist: {playlistDerived.name}",
      totalStepCount=jobStepCount,
      jobFn=jobFn
    )
    
    # return
    return job