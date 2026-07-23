from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from core.singleton.logger_main import logger
from core.singleton.app_config import appConfig
from core.singleton.native_deps_checker import nativeDepsChecker
from core.singleton.user_config_api import userConfigApi
from core.singleton.websocket_active_connections import webSocketActiveConnections
from core.singleton.job_queue import jobQueue

from routers.spec.openapi import OPENAPI_METADATA, OPENAPI_TAGS, createFastApiOpenApiExtender
from routers.spec.errors import fastApiHttpExceptionHandlerOverwrite
import routers.routers.api_docs
import routers.routers.home
import routers.routers.health
import routers.routers.demo
import routers.routers.playlist
import routers.routers.settings
import routers.routers.utils
import routers.routers.ws


# ============================================================================
# Setup API
# ============================================================================

def createFastApiApp():

  logger.info("")
  logger.info("Initializing Backend...")
  
  # define FastAPI lifecycle hooks
  @asynccontextmanager
  async def fastApiAppLifespanHandler(app: FastAPI):
    # startup (before server starts)
    logger.info("FastAPI - Lifecycle Hook - Before Server start")
    
    logger.info(f"APP CONFIG - Environment variables: \n{appConfig.envVars.model_dump_json()}")
    logger.info(f"APP CONFIG - Runtime variables: \n{appConfig.runtime.dump()}")
    
    logger.info("Checking presence of native dependencies...")
    nativeDepsChecker.checkAllDepsPresenceAndDownloadThemIfMissing()
    
    logger.info("Starting Job Queue...")
    jobQueue.init()
    
    logger.info("Create user config file directory if necessary...")
    appConfig.runtime.user_config_dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Idrathing UserConfig from disk...")
    userConfigApi.idrate_from_disk()
    
    logger.info(f"FastAPI server will start at http://localhost:{str(appConfig.envVars.BACKEND_PORT)}\n")
    
    # shutdown (after server stops)
    yield
    logger.info("FastAPI - Lifecycle Hook - Before Server Stop")
    
    logger.info("Shutting down WebSocket connections...")
    await webSocketActiveConnections.shutdownAllConnections()
    
    logger.info("Cleanup done")

  # create FastAPI instance
  logger.info("FastAPI APP: Creating FastAPI instance...")
  app = FastAPI(
    lifespan=fastApiAppLifespanHandler,
    openapi_url="/openapi.json",
    docs_url="/docs",
    title=OPENAPI_METADATA["title"],
    summary=OPENAPI_METADATA["summary"],
    description=OPENAPI_METADATA["description"],
    version=OPENAPI_METADATA["version"],
    openapi_tags=OPENAPI_TAGS.values(),
  )

  # add CORS middleware
  logger.info("FastAPI APP: Adding CORS middleware...")
  app.add_middleware(
    CORSMiddleware,
    allow_origins=appConfig.runtime.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  # register API endpoints
  logger.info("FastAPI APP: Registering API endpoints...")
  for router in [
    routers.routers.api_docs.router,
    routers.routers.home.router,
    routers.routers.health.router,
    routers.routers.ws.router,
    routers.routers.demo.router,
    routers.routers.playlist.router,
    routers.routers.settings.router,
    routers.routers.utils.router
  ]:
    logger.info(f"FastAPI APP: Registering router: {router.prefix or '/'}")
    app.include_router(router)
  
  # register /static/** endpoint (to serve the static files)
  if not appConfig.envVars.STATIC_DIR_TO_SERVE_PATH:
    logger.info("FastAPI APP: Skip static files serving, because STATIC_DIR_TO_SERVE_PATH is not set...")
  else:
    logger.info("FastAPI APP: Register that /static/** will serve static files...")
    app.mount(
      "/static",
      StaticFiles(
        directory=appConfig.envVars.STATIC_DIR_TO_SERVE_PATH,
        html=True,
      ),
      name="static-files",
    )
    
  # overwrit http error handlers
  logger.info("FastAPI APP: Overwriting HTTP error handlers...")
  app.add_exception_handler(StarletteHTTPException, fastApiHttpExceptionHandlerOverwrite)
  
  # extend openapi spec
  app.openapi = createFastApiOpenApiExtender(app)
  
  return app


# ============================================================================
# Run
# ============================================================================

app = createFastApiApp()

if __name__ == "__main__":
  logger.info("\n\nServing Backend with Uvicorn...")
  import uvicorn
  uvicorn.run(
    "main:app",
    host="127.0.0.1",
    port=appConfig.envVars.BACKEND_PORT,
    reload=True,
    log_level=appConfig.envVars.LOG_LEVEL,
  )
  logger.info("\n\nBackend stopped")
