from models.new import TrackDerived, PlaylistDerived
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
    tracksDerived = playlistDerived.model_copy(deep=True).tracks
    jobStepCount = len(tracksDerived)
    # crate job fn
    async def jobFn(job: Job):
      for trackDerived in tracksDerived:
        mustBeDownloaded = trackDerived.youtube_url and not trackDerived.has_disk_file
        if mustBeDownloaded:
          UtilsYoutubeFetcherApi.downloadYoutubeTrackAsMp3(trackDerived)
        job.incrementStep()

    # create job
    job = Job(
      title=f"Playlist Download All Tracks\nPlaylist: {playlistDerived.name}",
      totalStepCount=jobStepCount,
      jobFn=jobFn
    )
    return job