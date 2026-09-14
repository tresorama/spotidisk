import asyncio
from typing import Any, Callable, Coroutine, Literal


class UtilsBackgroundJob:
  """
  Run an async function as background job.  
  This class is an abstraction of `asyncio.create_task()` with auto clean up on completion.
  """
  def __init__(
    self,
    fn: Callable[[], Coroutine[Any, Any, None]] | Coroutine[Any, Any, None],
  ):
    # save fn
    self.fn  = fn
    # init state
    self._asyncioTask: asyncio.Task | None = None
    self.status: Literal["WAITING", "RUNNING", "DONE_OK", "DONE_ERROR"] = "WAITING"
    self.error: BaseException | None = None
    # init callbacks
    self._onComplete: Callable[[], None] | None = None
    
  def setCallback_onComplete(
    self, 
    callback: Callable[[], None] | None
  ):
    self._onComplete = callback
    
  def run(self):
    """Run the job"""
    # 1. create "ayncio.task"
    # - if fn is a functin...
    if callable(self.fn): self._asyncioTask = asyncio.create_task(self.fn())
    # - if fn is a coroutine object... 
    else: self._asyncioTask = asyncio.create_task(self.fn)
    # 2. set instance state
    self.status = "RUNNING"
    # 3. add done callback
    self._asyncioTask.add_done_callback(self.cleanUp)
    
  def cleanUp(self, task: asyncio.Task):
    # 1. get "ayncio.task" state (if success/error)
    taskException = task.exception()
    # 2. set instance state
    if taskException:
      self._asyncioTask = None
      self.status = "DONE_ERROR"
      self.error = taskException
    else:
      self._asyncioTask = None
      self.status = "DONE_OK"
      self.error = None
    # 3. call callback
    if self._onComplete: 
      self._onComplete()