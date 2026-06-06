from fastapi import APIRouter, WebSocket
from core.singleton.logger import logger

router = APIRouter(prefix="/ws", tags=["ws"])

# ============================================================================
# WebSocket for real-time updates
# ============================================================================

@router.websocket("/progress")
async def websocket_progress(websocket: WebSocket):
    """WebSocket for real-time download progress"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: Implement - send progress updates
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
