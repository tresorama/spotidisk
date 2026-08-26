from core.singleton.logger import loggerUserConfigApi
from core.singleton.app_config import appConfig

from core.classes.data.user_config_api import UserConfigApi

# init singletons

userConfigApi = UserConfigApi(
  logger=loggerUserConfigApi,
  config_file=appConfig.runtime.user_config_file_path
)