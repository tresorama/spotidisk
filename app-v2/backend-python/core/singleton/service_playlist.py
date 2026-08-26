from core.singleton.logger import loggerServicePlaylist
from core.singleton.app_config import appConfig
from core.singleton.user_config_api import userConfigApi
from core.singleton.native_deps_checker import nativeDepsChecker
from core.singleton.db import db
from core.singleton.job_queue import jobQueue
from core.singleton.websocket_event_emitter import webSocketEventEmitter

from core.classes.services.service_playlist import ServicePlaylist

servicePlaylist = ServicePlaylist(
  logger=loggerServicePlaylist,
  userConfigApi=userConfigApi,
  db=db,
  appConfig=appConfig,
  nativeDepsChecker=nativeDepsChecker,
  webSocketEventEmitter=webSocketEventEmitter,
  jobQueue=jobQueue,
)