import logging
from logging import Logger

class LoggerFactory:
  @staticmethod
  def create(name: str) -> Logger:
    # get/create instance
    logger = logging.getLogger(name)
    
    # if logger already has handlers, return it
    if logger.handlers:
      return logger
    
    # configure logger
    handler = logging.StreamHandler()
    handler.setFormatter(
      # logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
      logging.Formatter("%(levelname)s [%(name)s] %(message)s")
    )
    logger.addHandler(handler)
    logger.propagate = False

    return logger