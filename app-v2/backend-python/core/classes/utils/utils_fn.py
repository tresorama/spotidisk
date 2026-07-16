import time
from typing import Callable

class UtilsFn:
  @staticmethod
  def retryFn(
    fn: Callable,
    maxRetries: int = 3,
    retryDelay: float = 0.0,
  ): 
    """Retry a function multiple times if raises an exception."""
    for attempt in range(1, maxRetries + 1):
      try:
        print(f"Attempt {attempt}/{maxRetries}")
        return fn()
      except Exception as e:
        print(f"Attempt {attempt}/{maxRetries} - ERROR")
        if attempt < maxRetries:
          time.sleep(retryDelay)
        else:
          print(f"Attempt {attempt}/{maxRetries} - ERROR AND MAX REACHED -> RAISING EXCEPTION")
          raise e