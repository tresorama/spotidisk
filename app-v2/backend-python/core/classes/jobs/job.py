import asyncio
from typing import Callable, Awaitable, Literal, TypedDict

from core.classes.logger.logger import LoggerFactory


logger = LoggerFactory.create(name="Job")

# job id genrator class + singleton instance
class JobIdGenerator:
  def __init__(self):
    self.id = 0
  def generate(self):
    self.id += 1
    return self.id

jobIdGenerator = JobIdGenerator()

# internal types

JobStatus = Literal[
  "WAITING_START",
  "RUNNING",
  "COMPLETED",
  "CANCELED",
  "ERRORED"
]

class JobState(TypedDict):
  id: str
  title: str
  stepsTotal: int
  progress: float
  status: JobStatus
  stepsCompleted: int
  messages: list[str]
  

class JobExpectionCanceled(Exception):
  pass
class JobExpectionErrored(Exception):
  pass

# main class

class Job:
  """Job Definition Object"""
  def __init__(
    self, 
    title: str, 
    totalStepCount: int,
    jobFn: Callable[["Job"], Awaitable[None]]
  ):
    # save config
    self.title: str = title
    self.stepsTotal: int = totalStepCount
    self.jobFn: Callable[["Job"], Awaitable[None]] = jobFn
    # init rest of state
    self.id: str = str(jobIdGenerator.generate())
    self.stepsCompleted: int | None = None
    self.isCanceled: bool = False
    self.isErrored: bool = False
    self.error: Exception | None = None
    self.messages: list[str] = []
    # init lifecycle callbacks
    self.callback_beforeJobStart: Callable[["Job"], None] | None = None
    self.callback_afterIncrementStep: Callable[["Job"], None] | None = None
    self.callback_afterJobFinished: Callable[["Job"], None] | None = None
    
  # prepare job
  
  def setCallback_beforeJobStart(self, callback: Callable[["Job"], None] | None):
    self.callback_beforeJobStart = callback
    
  def setCallback_afterIncrementStep(self, callback: Callable[["Job"], None] | None):
    self.callback_afterIncrementStep = callback
  
  def setCallback_afterJobFinished(self, callback: Callable[["Job"], None] | None):
    self.callback_afterJobFinished = callback
    
  # get job state
  
  def getExecutionStatus(self) -> JobStatus:
    if self.isCanceled: return "CANCELED"
    if self.isErrored: return "ERRORED"
    if self.stepsCompleted is None: return "WAITING_START"
    if self.stepsCompleted >= 0 and self.stepsCompleted < self.stepsTotal: return "RUNNING"
    return "COMPLETED"
  
  def getProgress(self) -> float:
    progress: float = 0.0
    status = self.getExecutionStatus()
    if status == "WAITING_START": 
      progress = 0.0
    elif status == "COMPLETED": 
      progress = 1.0
    else:
      progress = ((self.stepsCompleted or 0) / self.stepsTotal)
    return progress
  
  def getStateAsJson(self) -> JobState:
    state: JobState = {
      "id": self.id,
      "title": self.title,
      "stepsTotal": self.stepsTotal,
      "progress": self.getProgress(),
      "status": self.getExecutionStatus(),
      "stepsCompleted": self.stepsCompleted or 0,  
      "messages": self.messages,
    }
    return state
  
  # run job fn
    
  async def runJobFn(self):
    # reset state
    self.stepsCompleted = 0
    self.isCanceled = False
    self.isErrored = False
    self.messages = []
    self.error = None
    # run
    try:
      # call callback
      self.onBeforeJobStart()
      # run
      await asyncio.sleep(0.05)
      await self.jobFn(self)
      await asyncio.sleep(0.05)
      # call callback
      self.onAfterJobFinished()
    # handle exceptions
    except JobExpectionCanceled as e:
      logger.error(f"Job {self.title} - CANCEL triggered: {e}")
      self.isCanceled = True
      self.messages.append("CANCELED BY USER")
      self.onAfterJobFinished()
    except (JobExpectionErrored, Exception) as e: 
      logger.error(f"Job {self.title} - ERROR triggered: {e}")
      self.isErrored = True
      self.error = e
      self.messages.append(str(f"ERROR: {e}"))
      self.onAfterJobFinished()
  
  # utils used by jobFn
  
  def triggerCancel(self):
    """Lifecycle Action - call this to raise an error that will CANCEL the job"""
    raise JobExpectionCanceled()
  def triggerError(self, name: str):
    """Lifecycle Action - call this to raise an error that will ERROR the job"""
    raise JobExpectionErrored(name)
    
  async def incrementStepCompleted(self):
    """Lifecycle Action - call this to mark step as completed"""
    # update state
    if self.stepsCompleted is None: 
      self.stepsCompleted = 1
    else: 
      self.stepsCompleted += 1
    # call callback
    await asyncio.sleep(0.1)
    self.onAfterIncrementStep()
      
  async def captureMessage(self, kind: Literal["ERROR","INFO"], message: str):
    """Lifecycle Action - call this to signal a message"""
    self.messages.append(f"{kind}: {message}")
    
  # lifecycle callback
  
  def onBeforeJobStart(self):
    if self.callback_beforeJobStart: self.callback_beforeJobStart(self)
    
  def onAfterIncrementStep(self):
    if self.callback_afterIncrementStep: self.callback_afterIncrementStep(self)
  
  def onAfterJobFinished(self):
    if self.callback_afterJobFinished: self.callback_afterJobFinished(self)
    
