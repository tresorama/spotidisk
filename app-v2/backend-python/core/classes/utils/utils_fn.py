import time
from typing import Callable

class UtilsFn:
  @staticmethod
  def retryFn(
    fn: Callable,
    maxRetries: int = 3,
    retryDelay: float = 0.0,
  ): 
    """
    Run a function with a `Retry-if-error-raised` strategy.  
    - If call is ok, return the result, 
    - if error is raised and maxRetries is not reached -> retry again after a delay,
    - if error is raised and maxRetries is reached -> raise the last error.
    """
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