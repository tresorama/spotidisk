class UtilsTrackDisk:
  @staticmethod
  def deriveTrackFilePath(title: str,artist: str,index: int, fileExtension: str,pattern: str) -> str:
    clean_title = title.replace("/","").replace("\\","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
    clean_artist = artist.replace("/","").replace("\\","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
    clean_index = str(index+1).zfill(2)
    clean_extension = "." + fileExtension.replace(".","")
    resolved = pattern.replace("{title}",clean_title).replace("{artist}",clean_artist).replace("{index:02d}",clean_index)
    resolved = resolved + clean_extension
    return resolved
  