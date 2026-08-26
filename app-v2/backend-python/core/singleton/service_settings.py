from core.singleton.db import db

from core.classes.services.service_settings import ServiceSettings

serviceSettings = ServiceSettings(
  db=db,
)