from core.singleton.logger import loggerWSEventEmitter
from core.singleton.websocket_active_connections import webSocketActiveConnections

from core.classes.notifications.websocket_event_emitter import WebSocketEventEmitter

# init singleton

webSocketEventEmitter = WebSocketEventEmitter(
  logger=loggerWSEventEmitter,
  webSocketActiveConnections=webSocketActiveConnections
)