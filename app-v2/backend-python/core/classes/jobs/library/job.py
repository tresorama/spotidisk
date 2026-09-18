
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Literal, TypedDict

from core.classes.utils.utils_time import UtilsTime

# types - job context

class JobContextAbstract(ABC):
  @abstractmethod
  def triggerJobCancel(self):
    """Cancel execution of job"""
    pass
  
  @abstractmethod
  def incrementStepCompleted(self):
    """Increment completed steps count"""
    pass
  
  @abstractmethod
  def addMessage(self, kind: Literal["ERROR","INFO"], message: str):
    """Add message to job"""
    pass

# types

JobId = str
JobFn = Callable[["Job", JobContextAbstract], Awaitable[None]]
JobStatus = Literal[
  "WAITING_START",
  "RUNNING",
  "COMPLETED",
  "CANCELED",
  "ERRORED",
]
JobStateDict = TypedDict("JobStateDict",{
  "id": JobId,
  "title": str,
  "stepsTotal": int,
  "status": JobStatus,
  "progress": float,
  "stepsCompleted": int,
  "messages": list[str],
  "error": Exception | None,
  "started_at": str | None,
  "finished_at": str | None,
})



# main class

class Job:
  """
  Instance of a Job.  
  Contains Job definition and keeps track of it's state during execution.
  **IMPORTANT**: do not create Job directly, use JobFactory.
  """
  def __init__(
    self,
    id: JobId,
    title: str,
    stepsTotal: int,
    jobFn: JobFn,
  ) -> None:
    # main state
    self.id: str = id
    self.title: str = title
    self.stepsTotal: int = stepsTotal
    self.jobFn: JobFn = jobFn
    # extra state
    self.stepsCompleted: int | None = None
    self.isCanceled: bool = False
    self.isErrored: bool = False
    self.error: Exception | None = None
    self.started_at: str | None = None
    self.finished_at: str | None = None
    self.messages: list[str] = []
    # set status to WAITING_START
    self.markAsWaitingStart()
    
  @property
  def status(self) -> JobStatus:
    if self.isCanceled: return "CANCELED"
    if self.isErrored: return "ERRORED"
    if self.stepsCompleted is None: return "WAITING_START"
    if self.stepsCompleted >= 0 and self.stepsCompleted < self.stepsTotal: return "RUNNING"
    return "COMPLETED"
  @property
  def progress(self) -> float:
    if self.stepsCompleted is None: return 0
    return self.stepsCompleted / self.stepsTotal
  
  # update state methods
  def markAsWaitingStart(self):
    self.stepsCompleted = None
    self.isCanceled = False
    self.isErrored = False
    self.error = None
    self.started_at = None
    self.finished_at = None
  def markAsRunning(self):
    self.started_at = UtilsTime.getCurrentDateTimeIso()
    self.stepsCompleted = 0
  def markAsStepCompleted(self):
    if self.stepsCompleted is None:
      self.stepsCompleted = 1
    else: 
      self.stepsCompleted += 1
  def markAsCompleted(self):
    self.finished_at = UtilsTime.getCurrentDateTimeIso()
    self.messages.append("COMPLETED")
  def markAsCanceled(self):
    self.finished_at = UtilsTime.getCurrentDateTimeIso()
    self.isCanceled = True
    self.messages.append("CANCELED")
  def markAsErrored(self, error: Exception):
    self.finished_at = UtilsTime.getCurrentDateTimeIso()
    self.isErrored = True
    self.error = error
    self.messages.append(f"ERRORED - {str(error)}")
  def addMessage(self, message: str):
    self.messages.append(message)    
    
  # readers
  def toDict(self) -> JobStateDict:
    return {
      "id": self.id,
      "title": self.title,
      "stepsTotal": self.stepsTotal,
      "status": self.status,
      "progress": self.progress,
      "stepsCompleted": self.stepsCompleted if self.stepsCompleted is not None else 0,
      "messages": self.messages,
      "error": self.error,
      "started_at": self.started_at,
      "finished_at": self.finished_at,
    }


