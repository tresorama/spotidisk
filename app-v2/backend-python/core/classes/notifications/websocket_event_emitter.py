from fastapi import WebSocket
from models.new import WsBackendEvent, WsBackendEventPayload
from core.singleton.logger import logger
from core.classes.utils.utils_time import UtilsTime

class WebSocketEventEmitter:
  """Object that emits events to connected websockets clients"""
  ws: None | WebSocket = None
  
  def setWebSocketConnection(self, ws: WebSocket):
    self.ws = ws
  def clearWebSocketConnection(self):
    self.ws = None
    
  async def emit(self, eventPayload: WsBackendEventPayload):
    ws = self.ws
    
    # ensure ws is connected
    if not ws:
      logger.error("WebSocketEventEmitter - emit - ws not connected, cannot emit event!")
      return
    
    # send event
    event = WsBackendEvent(
      dateTimeISO=UtilsTime.getCurrentDateTimeIso(),
      payload=eventPayload
    )
    try:
      await ws.send_json(event.model_dump())
      logger.info(f"WebSocketEventEmitter - emit - event sent: {event}")
    except Exception as e:
      logger.error(f"WebSocketEventEmitter - emit - error sending event: {e}")