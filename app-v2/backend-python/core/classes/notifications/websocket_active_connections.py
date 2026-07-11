from fastapi import WebSocket
from typing import Set

from core.classes.logger.logger import Logger

class WebSocketActiveConnections: 
  def __init__(
    self,
    logger: Logger
  ):
    self.logger = logger
    self.connections: Set[WebSocket] = set()
  
  def getActiveConnections(self):
    """Return all connections"""
    return self.connections
  
  def appendConnection(self, connection: WebSocket):
    """Add a new connection to the set"""
    self.connections.add(connection)
    self.logger.debug(f"WebSocketActiveConnections - appendConnection - ADDED. Now {len(self.connections)} connections.")
    
  def removeConnection(self, connection: WebSocket):
    """Remove a connection from the set"""
    self.connections.remove(connection)
    self.logger.debug(f"WebSocketActiveConnections - removeConnection - REMOVED. Now {len(self.connections)} connections.")
  
  async def shutdownAllConnections(self):
    """Close all connections. Call this when server is shutting down"""
    for connection in self.connections:
      try:
        await connection.close(code=1001)
      except Exception as e:
        self.logger.error(f"WebSocketActiveConnections - shutdownAllConnections - error closing connection: {e}")