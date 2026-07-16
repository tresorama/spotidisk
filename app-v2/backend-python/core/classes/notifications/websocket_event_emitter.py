from models.new import WsBackendEvent, WsBackendEventPayload

from core.classes.logger.logger import Logger
from core.classes.notifications.websocket_active_connections import WebSocketActiveConnections
from core.classes.utils.utils_time import UtilsTime

class WebSocketEventEmitter:
  """Object that emits events to connected websockets clients"""
  def __init__(
    self,
    logger: Logger,
    webSocketActiveConnections: WebSocketActiveConnections
  ):
    self.logger = logger
    self.webSocketActiveConnections: WebSocketActiveConnections = webSocketActiveConnections
    
  async def emit(self, eventPayload: WsBackendEventPayload):
    connections = self.webSocketActiveConnections.getActiveConnections()
    
    # send event
    for ws in connections:
      self.logger.debug(f"WebSocketEventEmitter - emit - sending event to client")
      try:
        event = WsBackendEvent(
          dateTimeISO=UtilsTime.getCurrentDateTimeIso(),
          payload=eventPayload
        )
        await ws.send_json(event.model_dump())
        self.logger.debug(f"WebSocketEventEmitter - emit - event sent: {event}")
      except Exception as e:
        self.logger.error(f"WebSocketEventEmitter - emit - error sending event: {e}")