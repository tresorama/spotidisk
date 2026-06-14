import yt_dlp 
from models.new import TrackDerived, TrackRaw
from core.singleton.logger import logger
from core.classes.utils_youtube import UtilsYoutube

class UtilsYoutubeFetcherApi:
  @staticmethod
  def findYoutubeUrlOfTrack(trackRaw: TrackRaw) -> str | None:
    """Find YouTube URL of track (Auto-Search URL)"""
    # define search query
    searchQuery = f"{trackRaw.artists} {trackRaw.title}"
    
    # init client options
    ydl_opts: yt_dlp._Params = {
      'quiet': True,
      'no_warnings': True,
      'default_search': 'ytsearch1',  # Retutns only first match
      'extract_flat': True,
    }
    
    # search
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(
        searchQuery,
        download=False
      )
            
    # extract the first track found
    if info and 'entries' in info and len(info['entries']) > 0:
      first_result = info['entries'][0]
      itemData ={
        'video_url': f"https://www.youtube.com/watch?v={first_result['id']}",
        'title': first_result.get('title', 'Unknown'),
        'duration': first_result.get('duration', 0),
      }
      return itemData['video_url']
    else:
      return None
  
  @staticmethod
  def downloadYoutubeTrackAsMp3(trackDerived: TrackDerived) -> bool:
    """Download track from YouTube as MP3 and save to disk"""
    return False