from pathlib import Path
import subprocess
from core.classes.utils_os import UtilsOS
    
class UtilsDisk:
  """Utilities for working with the OS disk"""
  @staticmethod
  def revealFolderInOS(folderPath: str) -> None:
    osType = UtilsOS.getOsType()
    path = Path(folderPath).resolve()
    # macOS
    if osType == "MAC_OS":  
      subprocess.run(["open", "-R", str(path)])
    # Windows
    elif osType == "WINDOWS":  
      subprocess.run(["explorer", "/select,", str(path)])
    # Linux
    else: 
      subprocess.run(["xdg-open", str(path.parent)])