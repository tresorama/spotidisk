from core.singleton.logger import loggerServiceDemo
from core.singleton.websocket_event_emitter import webSocketEventEmitter
from core.singleton.jobs import jobFactory

from core.classes.services.service_demo import ServiceDemo

serviceDemo = ServiceDemo(
  logger=loggerServiceDemo,
  webSocketEventEmitter=webSocketEventEmitter,
  jobFactory=jobFactory,
)