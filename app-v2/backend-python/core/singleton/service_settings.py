from core.singleton.db import db
from core.singleton.user_config_api import userConfigApi
from core.singleton.service_playlist import servicePlaylist

from core.classes.services.service_settings import ServiceSettings

serviceSettings = ServiceSettings(
  db=db,
  userConfigApi=userConfigApi,
  servicePlaylist=servicePlaylist,
)