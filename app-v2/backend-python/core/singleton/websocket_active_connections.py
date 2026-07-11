from core.singleton.logger import loggerWSActiveConnections

from core.classes.notifications.websocket_active_connections import WebSocketActiveConnections

# init singleton

webSocketActiveConnections = WebSocketActiveConnections(
  logger=loggerWSActiveConnections,
)