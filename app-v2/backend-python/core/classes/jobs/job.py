import asyncio
from typing import Awaitable, Callable, Literal

from core.classes.logger.logger import LoggerFactory

logger = LoggerFactory.create(name="Job")

JobExecutionStatus = Literal[
  "WAITING_START",
  "RUNNING",
  "COMPLETED",
  "CANCELED",
  "ERRORED",
]


class Job:
  """Definition and runtime state of a single job."""

  def __init__(
    self,
    title: str,
    totalStepCount: int,
    jobFn: Callable[["Job"], Awaitable[None]],
  ):
    self.title = title
    self.stepsTotal = totalStepCount
    self.jobFn = jobFn

    self.id: str | None = None
    self.stepsCompleted = 0
    self.isCanceled = False
    self.isErrored = False
    self.error: Exception | None = None
    self.messages: list[str] = []
    self._cancelRequested = False

    self.callback_beforeJobStart: Callable[["Job"], None] | None = None
    self.callback_afterIncrementStep: Callable[["Job"], None] | None = None
    self.callback_afterJobCompleted: Callable[["Job"], None] | None = None
    self.callback_afterJobCanceled: Callable[["Job"], None] | None = None
    self.callback_afterJobErrored: Callable[["Job"], None] | None = None

  def setCallback_beforeJobStart(self, callback: Callable[["Job"], None] | None):
    self.callback_beforeJobStart = callback

  def setCallback_afterIncrementStep(self, callback: Callable[["Job"], None] | None):
    self.callback_afterIncrementStep = callback

  def setCallback_afterJobCompleted(self, callback: Callable[["Job"], None] | None):
    self.callback_afterJobCompleted = callback

  def setCallback_afterJobCanceled(self, callback: Callable[["Job"], None] | None):
    self.callback_afterJobCanceled = callback

  def setCallback_afterJobErrored(self, callback: Callable[["Job"], None] | None):
    self.callback_afterJobErrored = callback

  def getExecutionStatus(self) -> JobExecutionStatus:
    if self.isCanceled:
      return "CANCELED"
    if self.isErrored:
      return "ERRORED"
    if self.stepsCompleted >= self.stepsTotal:
      return "COMPLETED"
    if self.stepsCompleted > 0:
      return "RUNNING"
    return "WAITING_START"

  def getProgress(self) -> float:
    if self.stepsTotal <= 0:
      return 1.0
    return min(self.stepsCompleted / self.stepsTotal, 1.0)

  def isCancellationRequested(self) -> bool:
    return self._cancelRequested

  async def runJobFn(self):
    self.stepsCompleted = 0
    self.isCanceled = False
    self.isErrored = False
    self.messages = []
    self.error = None

    try:
      self.onBeforeJobStart()

      if self._cancelRequested:
        self.cancelExecution()
        return

      await self.jobFn(self)

      if self._cancelRequested:
        self.cancelExecution()
        return

      self.onAfterJobCompleted()
    except asyncio.CancelledError:
      self.cancelExecution()
    except Exception as e:
      self.onJobErrored(e)

  def requestCancellation(self):
    """Request cooperative cancellation without running lifecycle callbacks."""
    self._cancelRequested = True

  def cancelExecution(self):
    if self.isCanceled:
      return

    self.isCanceled = True
    self._cancelRequested = True
    self.messages.append("CANCELED BY USER")
    self.onAfterJobCanceled()

  async def incrementStepCompleted(self):
    if self._cancelRequested:
      raise asyncio.CancelledError

    self.stepsCompleted += 1
    self.onAfterIncrementStep()

  async def captureMessage(self, kind: Literal["ERROR", "INFO"], message: str):
    self.messages.append(f"{kind}: {message}")

  def raiseError(self, name: str):
    raise Exception(name)

  def onBeforeJobStart(self):
    if self.callback_beforeJobStart:
      self.callback_beforeJobStart(self)

  def onAfterIncrementStep(self):
    if self.callback_afterIncrementStep:
      self.callback_afterIncrementStep(self)

  def onAfterJobCompleted(self):
    if self.callback_afterJobCompleted:
      self.callback_afterJobCompleted(self)

  def onAfterJobCanceled(self):
    if self.callback_afterJobCanceled:
      self.callback_afterJobCanceled(self)

  def onJobErrored(self, error: Exception):
    logger.error(f"Job {self.title} - exception raised from jobFn: {error}")
    self.isErrored = True
    self.error = error
    self.messages.append(f"ERROR: {error}")
    if self.callback_afterJobErrored:
      self.callback_afterJobErrored(self)
