from core.singleton.user_config_api import userConfigApi
from core.singleton.app_config import appConfig
from core.singleton.native_deps_checker import nativeDepsChecker

from core.classes.data.db import Db

db = Db(
  userConfigApi=userConfigApi,
  appConfig=appConfig,
  nativeDepsChecker=nativeDepsChecker
)