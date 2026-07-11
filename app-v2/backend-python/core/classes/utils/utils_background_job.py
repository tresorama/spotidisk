import asyncio
from typing import Any, Callable, Coroutine


class UtilsBackgroundJob:
  """
  Run an async function as background job.  
  This class is an abstraction of `asyncio.create_task()` with auto clean up on completion.
  """
  def __init__(
    self,
    fn: Callable[[], Coroutine[Any, Any, None]] | Coroutine[Any, Any, None]
  ):
    # save config
    self.fn  = fn
    # init instances
    self.task: asyncio.Task | None = None
    # init
    self.start()
    
  def start(self):
    # if fn is a functin...
    if callable(self.fn): self.task = asyncio.create_task(self.fn())
    # if fn is a coroutine object... 
    else: self.task = asyncio.create_task(self.fn)
    
    self.task.add_done_callback(self.clear)
    
  def clear(self, task: asyncio.Task):
    self.task = None