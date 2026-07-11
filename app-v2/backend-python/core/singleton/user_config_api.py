from core.singleton.logger import loggerUserConfigApi, loggerUserConfigReaderApi
from core.singleton.app_config import appConfig
from core.singleton.native_deps_checker import nativeDepsChecker

from core.classes.data.user_config_api import UserConfigApi, UserConfigReaderApi

# init singletons

userConfigApi = UserConfigApi(
  logger=loggerUserConfigApi,
  config_file=appConfig.runtime.user_config_file_path
)
userConfigReaderApi = UserConfigReaderApi(
  logger=loggerUserConfigReaderApi,
  userConfigApi=userConfigApi,
  appConfig=appConfig,
  nativeDepsChecker=nativeDepsChecker,
)