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
  def downloadYoutubeTrackAsMp3(trackDerived: TrackDerived):
    """Download track from YouTube as MP3 and save to disk"""
    
    # get track data
    rawYoutubeUrl = trackDerived.youtube_url
    diskFilePath = trackDerived.disk_file_path
    
    # abort if no YouTube URL
    if not rawYoutubeUrl:
      return (False,"NO_YOUTUBE_URL")
    
    # clean youtube url
    youtubeUrl = UtilsYoutube.cleanYoutubeVideoUrl(rawYoutubeUrl)
    
    # download
    try:
      ydl_opts: yt_dlp._Params = {
        'format': 'bestaudio/best',
        'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
        }],
        'outtmpl': diskFilePath,
        'quiet': False,
        'no_warnings': False,
        # === FIX PER PO TOKEN ===
        'extractor_args': {
          'youtube': {
            'player_client': ['web'],
            'po_token': [None],  # Permette a yt-dlp di generare automaticamente
          }
        },
        # Headers per evitare blocchi
        'http_headers': {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
        # Retry più aggressivi
        'retries': 5,
        'socket_timeout': 30,
        'sleep_interval': 1,
      }
        
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(youtubeUrl, download=True)
        return (True,"SUCCESS")
    except Exception as e:
      return (False,"ERROR_DOWNLOADING", e)