import logging
from core.singleton.config_static import config_static

# init
logging.basicConfig(
  level=config_static.log_level.upper(),
)
logger = logging.getLogger(name="main")
