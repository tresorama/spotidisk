from models.settings import SettingsMutable

from core.classes.data.db import Db

class ServiceSettings:
  
  def __init__(
    self,
    db: Db
  ):
    self.db = db
    
  def getSettings(self):
    dbReadResult = self.db.getSettings()
    return (True, "FOUND", dbReadResult)
  
  def updateSettings(self, payload: SettingsMutable):
    dbUpdateResult = self.db.updateSettings(newSettingsMutable=payload)
    if dbUpdateResult[0] == False:
      return (False, "DB_UPDATE_ERROR", dbUpdateResult[1])
    return (True, "UPDATED")
  