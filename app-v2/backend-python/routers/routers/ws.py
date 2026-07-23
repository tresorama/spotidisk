from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..spec.openapi import OPENAPI_TAG_NAME

from models.ws import WsBackendEventPayloadTypeMessage

from core.singleton.logger import loggerWS as logger
from core.singleton.websocket_event_emitter import webSocketEventEmitter
from core.singleton.websocket_active_connections import webSocketActiveConnections
from core.singleton.job_queue import jobQueueLifecycleEffect_webSocketNotifier

router = APIRouter(
  prefix="/ws", 
  tags=[OPENAPI_TAG_NAME.WS],
  include_in_schema=False
)

# ============================================================================
# WebSocket for real-time updates
# ============================================================================

@router.websocket("/entry-point")
async def webSocketEntryPoint(websocket: WebSocket):
  """
  WebSocket endpoint use to push real-time updates from backend to frontend.
  We push various message types to frontend.
  """
  logger.info("/ws/entry-point - Client asked to connect")
  
  # accept connection
  await websocket.accept()
  logger.info("/ws/entry-point - Client connected")
  
  # set connection to singleton instance
  webSocketActiveConnections.appendConnection(websocket)
  
  # send job queue progress
  jobQueueLifecycleEffect_webSocketNotifier._notifyJobProgress()
  # send a welcome message
  await webSocketEventEmitter.emit(
    eventPayload=WsBackendEventPayloadTypeMessage(
      text="Hello from backend!"
    )
  )
  
  # loop for ever
  tickCount = 0
  while True:
    try:
      tickCount += 1
      logger.debug(f"/ws/entry-point - While loop tick {tickCount}")
      await websocket.receive()
    except WebSocketDisconnect:
      logger.info("/ws/entry-point - Connection closed from client (WebSocketDisconnect)")
      webSocketActiveConnections.removeConnection(websocket)
      break
    except Exception as e:
      logger.info("/ws/entry-point - Unexpected error (Exception). Closing connection!")
      webSocketActiveConnections.removeConnection(websocket)
      break
    
  logger.info("/ws/entry-point - While loop ended")
