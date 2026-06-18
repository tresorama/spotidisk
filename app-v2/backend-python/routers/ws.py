import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.new import WsBackendEventPayloadTypeMessage
from core.singleton.logger import logger
from core.singleton.websocket_event_emitter import webSocketEventEmitter

router = APIRouter(prefix="/ws", tags=["ws"])

# ============================================================================
# WebSocket for real-time updates
# ============================================================================

@router.websocket("/entry-point")
async def webSocketEntryPoint(websocket: WebSocket):
  """
  WebSocket endpoint use to push real-time updates from backend to frontend.
  We don't push data, but only queryKey that are stale, so the frontend can invalidate them and reftch.
  """
  # accept connection
  await websocket.accept()
  logger.info("/ws/entry-point - Connection accepted")
  
  # set connection to singleton instance
  webSocketEventEmitter.setWebSocketConnection(websocket)
  
  # send a message
  await webSocketEventEmitter.emit(
    eventPayload=WsBackendEventPayloadTypeMessage(
      text="Hello from backend!"
    )
  )
  
  # loop for ever
  tickCount = 0
  tickDelay = 4
  try:
    while True:
      tickCount += 1
      logger.info(f"/ws/entry-point - While loop tick {tickCount}")
      await asyncio.sleep(tickDelay)
      # data = await websocket.receive_text()
  except WebSocketDisconnect:
    # disconnect
    await websocket.close()
    # remove connection from singleton instance
    webSocketEventEmitter.clearWebSocketConnection()
    logger.info("/ws/entry-point - Connection closed from client")
    return None
