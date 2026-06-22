from core.classes.data.user_config_api import UserConfigApi
from core.singleton.app_config import appConfigRuntime

# init singletons
userConfigApi = UserConfigApi(appConfigRuntime.user_config_file_path)