from core.singleton.logger import loggerNativeDepsChecker
from core.singleton.app_config import appConfig

from core.classes.utils.utils_native_deps_checker import UtilsNativeDepsChecker

# init singletons

nativeDepsChecker = UtilsNativeDepsChecker(
  logger=loggerNativeDepsChecker,
  location1LocalBinFolderPath=str(appConfig.runtime.binaries_path)
)