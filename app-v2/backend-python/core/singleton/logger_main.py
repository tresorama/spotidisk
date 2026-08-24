import logging
from core.singleton.app_config import appConfig
from core.classes.logger.logger import LoggerFactory

# configure th global logger config
logging.basicConfig(
  level=appConfig.envVars.LOG_LEVEL.upper(),
)

# init logger
logger = LoggerFactory.create(name="MAIN")

