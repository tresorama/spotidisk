import os
import shutil
import sys
import platform
from typing import  Literal
import urllib.request
from pathlib import Path
import urllib

from core.classes.logger.logger import Logger
from core.classes.utils.utils_disk import UtilsDisk
from core.classes.utils.utils_fn import UtilsFn

# main class

class UtilsNativeDepsChecker:
  """
  Class for checking Native Deps (ffmpeg, deno) installation status and trying to download them if missing.  
  Native Deps are used by other classes
  """
  def __init__(
    self,
    logger: Logger,
    location1LocalBinFolderPath: str
  ):
    self.logger: Logger = logger
    self.finder: DepsFinder = DepsFinder(
      logger=logger,
      location1DirPath=location1LocalBinFolderPath
    )
    self.downloader: DepsDownloader = DepsDownloader(
      logger=logger,
      downloadDirPath=location1LocalBinFolderPath
    )
    
  def checkAllDepsPresenceAndDownloadThemIfMissing(self):
    """ 
    Check that `ffmpeg`, `deno` are installed. If not installed, download them. If download failed, raise error
    """
    # 1. check FFmpeg
    self.logger.info("Checking presence of FFmpeg...")
    ffmpegPath = self.getFFmpegPath()
    if ffmpegPath:
      self.logger.info(f"Checking presence of FFmpeg: Already installed at: {ffmpegPath}")
    else:
      self.logger.info("Checking presence of FFmpeg: Not found, downloading...")
      self.downloadFFmpeg()
      ffmpegPath = self.getFFmpegPath()
      if not ffmpegPath:
        raise RuntimeError("Checking presence of FFmpeg: Not found, tried to download but failed!")
      
    # 2. check Deno
    self.logger.info("Checking presence of Deno...")
    denoPath = self.getDenoPath()
    if denoPath:
      self.logger.info(f"Checking presence of Deno: already installed at: {denoPath}")
    else:
      self.logger.info("Checking presence of Deno: Not found, downloading...")
      self.downloadDeno()
      denoPath = self.getDenoPath()
      if not denoPath:
        raise RuntimeError("Checking presence of Deno: Not found, tried to download but failed!")
  
  def getDenoPath(self):
    """Get Deno path in system, if installed"""
    return self.finder.findBinary(binName="deno")
  
  def getFFmpegPath(self):
    """Get FFmpeg path in system, if installed"""
    return self.finder.findBinary(binName="ffmpeg")
  
  def downloadDeno(self):
    """Download Deno to disk in local .bin folder"""
    self.downloader.downloadBinaryFileToPathBasedOnOs(
      URL_MAC_ARM64="https://github.com/denoland/deno/releases/download/v2.8.2/deno-aarch64-apple-darwin.zip",
      URL_MAC_X64="https://github.com/denoland/deno/releases/download/v2.8.2/deno-x86_64-apple-darwin.zip",
      URL_LINUX_ARM64="https://github.com/denoland/deno/releases/download/v2.8.2/deno-aarch64-unknown-linux-gnu.zip",
      URL_LINUX_X64="https://github.com/denoland/deno/releases/download/v2.8.2/deno-x86_64-unknown-linux-gnu.zip",
      URL_WIN_ARM64="https://github.com/denoland/deno/releases/download/v2.8.2/deno-aarch64-pc-windows-msvc.zip",
      URL_WIN_X64="https://github.com/denoland/deno/releases/download/v2.8.2/deno-x86_64-pc-windows-msvc.zip",
      BIN_NAME_MAC="deno",
      BIN_NAME_LINUX="deno",
      BIN_NAME_WIN="deno.exe",
    )
  
  def downloadFFmpeg(self):
    """Download FFmpeg to disk in local .bin folder"""
    self.downloader.downloadBinaryFileToPathBasedOnOs(
      URL_MAC_ARM64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-darwin-arm64",
      URL_MAC_X64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-darwin-x64",
      URL_LINUX_ARM64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-linux-arm64",
      URL_LINUX_X64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-linux-x64",
      URL_WIN_ARM64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-win32-x64",
      URL_WIN_X64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-win32-x64",
      BIN_NAME_MAC="ffmpeg",
      BIN_NAME_LINUX="ffmpeg",
      BIN_NAME_WIN="ffmpeg.exe",
    )
    self.downloader.downloadBinaryFileToPathBasedOnOs(
      URL_MAC_ARM64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-darwin-arm64",
      URL_MAC_X64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-darwin-x64",
      URL_LINUX_ARM64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-linux-arm64",
      URL_LINUX_X64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-linux-x64",
      URL_WIN_ARM64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-win32-x64",
      URL_WIN_X64="https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-win32-x64",
      BIN_NAME_MAC="ffprobe",
      BIN_NAME_LINUX="ffprobe",
      BIN_NAME_WIN="ffprobe.exe",
    )
  

# internals
  
class DepsFinder:
  location1DirPath: Path
  def __init__(
    self,
    logger: Logger,
    location1DirPath: str
  ): 
    self.logger = logger
    self.location1DirPath = Path(location1DirPath)
    
  def findBinary(self, binName: str):
    """
    Check if a binary is present in system, by checking locations in order:  
      1. local .bin folder
      2. bundled (for PyInstaller builds)
      3. common system path (hombrew, system, ...)
      4. system PATH  
    If not found, return `None`
    """
    finalPath: str | None = None
    
    # Get executable name based on OS
    executableName = f"{binName}.exe" if sys.platform == "win32" else binName
    
    # 1. Check local .bin folder
    self.logger.info(f"Location 1 (local bin folder)...")
    dirPath = self.location1DirPath
    finalPath = str(dirPath / executableName)
    self.logger.info(f"- Path: {finalPath}")
    if os.path.exists(finalPath):
      self.logger.info(f"  - Found: {finalPath}")
      return str(finalPath)
    self.logger.info(f"  - Not found")
    
    # 2. Check bundled first (for PyInstaller builds)
    self.logger.info(f"Location 2 (bundled with PyInstaller)...")
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", False):
      dirPath = sys._MEIPASS
      if sys.platform == "win32":
        finalPath = os.path.join(dirPath, binName, executableName)
      else:
        finalPath = os.path.join(dirPath, binName, executableName)
      self.logger.info(f"- Path: {finalPath}")
      if os.path.exists(finalPath):
        self.logger.info(f"  - Found: {finalPath}")
        return str(finalPath)
    else:
      self.logger.info(f"  - Skipped, is not PyInstaller build")
        
    # 3. Check common system paths (for homebrew/system installs)
    self.logger.info(f"Location 3 (common system paths)...")
    commonSystemPaths = [
      "/opt/homebrew/bin",  # macOS ARM homebrew
      "/usr/local/bin",  # macOS Intel homebrew / Linux
      "/usr/bin",  # Linux system
    ]
    for dirPath in commonSystemPaths:
      finalPath = os.path.join(dirPath, executableName)
      self.logger.info(f"- Path: {finalPath}")
      if os.path.exists(finalPath):
        self.logger.info(f"  - Found: {finalPath}")
        return str(finalPath)
      else:
        self.logger.info(f"  - Not found")

    # 4. Check if is in PATH (bin is in unknown path but is in PATH)
    self.logger.info(f"Location 4 (ffmpeg in PATH)...")
    finalPath = shutil.which(binName)
    if finalPath:
      self.logger.info(f"  - Found: {finalPath}")
      return finalPath
    self.logger.info(f"  - Not found")

    # not found
    return None
  
  
class DepsDownloader:
  def __init__(
    self, 
    logger: Logger,
    downloadDirPath: str
  ):
    self.logger: Logger = logger
    self.downloadDirPath: Path = Path(downloadDirPath)
    
  def downloadBinaryFileToPathBasedOnOs(
    self,
    URL_MAC_ARM64: str,
    URL_MAC_X64: str,
    URL_LINUX_ARM64: str,
    URL_LINUX_X64: str,
    URL_WIN_ARM64: str,
    URL_WIN_X64: str,
    BIN_NAME_MAC: str,
    BIN_NAME_LINUX: str,
    BIN_NAME_WIN: str,
  ): 
    """Download binary file to path based on OS, and make it executable"""
    
    DOWNLOAD_DIR_PATH = self.downloadDirPath
    
    # 1. derive OS and ARCH
    osName = platform.system()
    archName = platform.machine()
    self.logger.info(f"OS: {osName}\nARCH: {archName}")
    
    # 2. derive url, bin file name, 
    URL: str | None = None
    BIN_FILE_NAME: str | None = None
    if osName == "Darwin" and archName == "arm64":
      URL = URL_MAC_ARM64
      BIN_FILE_NAME = BIN_NAME_MAC
    elif osName == "Darwin" and archName == "x86_64":
      URL = URL_MAC_X64
      BIN_FILE_NAME = BIN_NAME_MAC
    elif osName == "Windows" and archName == "ARM64":
      URL = URL_WIN_ARM64
      BIN_FILE_NAME = BIN_NAME_WIN
    elif osName == "Windows" and archName == "AMD64":
      URL = URL_WIN_X64
      BIN_FILE_NAME = BIN_NAME_WIN
    elif osName == "Linux" and archName == "aarch64":
      URL = URL_LINUX_ARM64
      BIN_FILE_NAME = BIN_NAME_LINUX
    elif osName == "Linux" and archName == "x86_64":
      URL = URL_LINUX_X64
      BIN_FILE_NAME = BIN_NAME_LINUX
    
    if not URL:
      return (False, "UNSUPPORTED_OS", f"OS: {osName} ARCH: {archName}")
    if not BIN_FILE_NAME:
      return (False, "UNSUPPORTED_OS", f"OS: {osName} ARCH: {archName}")
    
    self.logger.info(f"URL: {URL}\nBIN_FILE_NAME: {BIN_FILE_NAME}")
    
    # 3. derive compression based on download url extension
    FILE_COMPRESSION: Literal["",".gz", ".zip", ".tar.gz"] = ""
    if URL.endswith(".gz"): FILE_COMPRESSION = ".gz"
    elif URL.endswith(".zip"): FILE_COMPRESSION = ".zip"
    elif URL.endswith(".tar.gz"): FILE_COMPRESSION = ".tar.gz"
    self.logger.info(f"FILE_COMPRESSION: {FILE_COMPRESSION or 'NO_COMPRESSION'}")
    
    # 4. create dir if not exists
    UtilsDisk.createDirIfNotExists(str(DOWNLOAD_DIR_PATH))
    
    # 5. download file
    DOWNLOAD_FILE_PATH = DOWNLOAD_DIR_PATH / f"{BIN_FILE_NAME}{FILE_COMPRESSION}"
    try:
      UtilsFn.retryFn(
        maxRetries=3,
        retryDelay=0.5,
        fn=lambda: urllib.request.urlretrieve(
          url=URL,
          filename=str(DOWNLOAD_FILE_PATH)
        ),
      )
    except Exception as e:
      self.logger.error(f"Failed to download file\nError: {e}")
      return (False, "FAILED_TO_DOWNLOAD", e)
    
    # 5. uncompress (if compressed)
    if FILE_COMPRESSION:
      self.logger.info(f"Uncompressing file: {DOWNLOAD_FILE_PATH}")
      try:
        shutil.unpack_archive(
          filename=str(DOWNLOAD_FILE_PATH),
          extract_dir=str(DOWNLOAD_DIR_PATH)
        )
        UtilsDisk.deleteFileIfExists(
          filePath=str(DOWNLOAD_FILE_PATH)
        )
      except Exception as e:
        self.logger.error(f"Failed to uncompress file\nError: {e}")
        return (False, "FAILED_TO_UNCOMPRESS", e)
      
    # 5. make executable
    BIN_FILE_PATH = DOWNLOAD_DIR_PATH / BIN_FILE_NAME
    self.logger.info(f"Making executable: {BIN_FILE_PATH}")
    UtilsDisk.makeExecutable(filePath=str(BIN_FILE_PATH))
    
    # 6. success
    return (True, "OK", BIN_FILE_PATH)
    
