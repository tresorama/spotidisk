import logging
from config import settings

# init
logging.basicConfig(
  level=settings.log_level.upper(),
)
logger = logging.getLogger(name="main")
