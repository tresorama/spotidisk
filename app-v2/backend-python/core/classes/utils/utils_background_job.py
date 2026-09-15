import asyncio
from typing import Any, Callable, Coroutine, Literal


class UtilsBackgroundJob:
  """Small lifecycle wrapper around an asyncio Task.

  Kept for compatibility with existing callers. New code should prefer
  asyncio.create_task() directly when this lifecycle state is not needed.
  """

  def __init__(
    self,
    fn: Callable[[], Coroutine[Any, Any, None]] | Coroutine[Any, Any, None],
  ):
    self.fn = fn
    self._asyncioTask: asyncio.Task | None = None
    self.status: Literal["WAITING", "RUNNING", "DONE_OK", "DONE_ERROR", "CANCELED"] = "WAITING"
    self.error: BaseException | None = None
    self._onComplete: Callable[[], None] | None = None

  def setCallback_onComplete(self, callback: Callable[[], None] | None):
    self._onComplete = callback

  def run(self):
    if self._asyncioTask is not None:
      raise RuntimeError("Background job is already running")

    if callable(self.fn):
      self._asyncioTask = asyncio.create_task(self.fn())
    else:
      self._asyncioTask = asyncio.create_task(self.fn)

    self.status = "RUNNING"
    self._asyncioTask.add_done_callback(self.cleanUp)

  def cancel(self):
    if self._asyncioTask is not None:
      self._asyncioTask.cancel()

  def cleanUp(self, task: asyncio.Task):
    self._asyncioTask = None

    if task.cancelled():
      self.status = "CANCELED"
      self.error = None
    else:
      taskException = task.exception()
      if taskException:
        self.status = "DONE_ERROR"
        self.error = taskException
      else:
        self.status = "DONE_OK"
        self.error = None

    if self._onComplete:
      self._onComplete()
