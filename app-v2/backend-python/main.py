from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.singleton.logger import logger
from core.singleton.app_config import appConfigStatic

# Import API Routers
from routers import (
  health,
  ws,
  demo,
  playlist,
)

# ============================================================================
# Setup API
# ============================================================================

logger.info("Starting Sunnify API...")

# api
logger.info("Crating FastAPI instance...")
app = FastAPI(
  title="Sunnify API",
  description="Spotify & YouTube music downloader",
  version="2.1.0",
  docs_url="/docs",
  openapi_url="/openapi.json",
)

# api CORS middleware
logger.info("Adding CORS middleware...")
app.add_middleware(
  CORSMiddleware,
  allow_origins=appConfigStatic.cors_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# register API endpoints
logger.info("Registering API endpoints...")
app.include_router(health.router)
app.include_router(ws.router)
app.include_router(demo.router)
app.include_router(playlist.router)

@app.on_event("startup")
async def startup():
  port=appConfigStatic.backend_port
  logger.info("Server started at http://127.0.0.1:" + str(port))


# ============================================================================
# Run
# ============================================================================

if __name__ == "__main__":
  logger.info("Starting Sunnify API with Uvicorn...")
  import uvicorn
  uvicorn.run(
    "main:app",
    host="127.0.0.1",
    port=appConfigStatic.backend_port,
    reload=appConfigStatic.debug,
    log_level=appConfigStatic.log_level,
  )
  logger.info("Sunnify API stopped")
