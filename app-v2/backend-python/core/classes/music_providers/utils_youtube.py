from urllib.parse import urlparse


class UtilsYoutube:
  @staticmethod
  def extractYoutubeVideoIdFromUrl(youtubeUrl: str) -> str:
    # urlparse -> scheme://netloc/path;parameters?query#fragment
    # query: v=XXXXXX&other=YYYYY
    # 
    # url shape 1: https://www.youtube.com/watch?v=65DsA5PZamU
    if "youtube.com/watch" in youtubeUrl:
      queryString = urlparse(youtubeUrl).query
      youtubeId = queryString.split("v=")[1].split("&")[0]
    # url shape 2: https://youtu.be/65DsA5PZamU
    else: 
      youtubeId = urlparse(youtubeUrl).path.split("/")[1]
    return youtubeId
  
  @staticmethod
  def cleanYoutubeVideoUrl(youtubeUrl: str) -> str:
    youtubeId = UtilsYoutube.extractYoutubeVideoIdFromUrl(youtubeUrl)
    return f"https://www.youtube.com/watch?v={youtubeId}"