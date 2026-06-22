import datetime

class UtilsTime:
  @staticmethod
  def getCurrentDateTimeIso():
    """Return current date and time in ISO format (2020-01-01T00:00:00.000Z)"""
    return datetime.datetime.now().isoformat()