import datetime

class UtilsTime:
  @staticmethod
  def getCurrentDateTimeIso():
    """Return current date and time in ISO format (2020-01-01T00:00:00.000Z)"""
    return datetime.datetime.now().isoformat()
  
  @staticmethod
  def formatDurationInSecondsToMMSS(durationInSeconds: float):
    """Return duration in seconds as a string in the format "mm:ss"."""
    mm = int(durationInSeconds // 60)
    ss = int(durationInSeconds % 60)
    return f"{mm:02d}:{ss:02d}"
    
    
    
class UtilsTimeExecutionTimer:
  startTime: datetime.datetime | None = None
  def start(self):
    self.startTime = datetime.datetime.now()
  def end(self):
    if not self.startTime: raise Exception("Execution timer not started")
    delta = datetime.datetime.now() - self.startTime
    return UtilsTime.formatDurationInSecondsToMMSS(delta.total_seconds())