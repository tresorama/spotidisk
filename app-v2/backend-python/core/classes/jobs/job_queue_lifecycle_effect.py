from abc import ABC, abstractmethod

from core.classes.jobs.job import Job
from core.classes.jobs.job_queue import JobQueue

class JobQueueLifecycleEffect(ABC):
  
  jobQueue: JobQueue
  
  @abstractmethod
  def onAfterInit(self):
    pass
  
  @abstractmethod
  def onAfterJobQueued(self, job: Job):
    pass
  
  @abstractmethod
  def onBeforeJobStart(self, job: Job):
    pass
    
  @abstractmethod
  def onAfterIncrementStep(self, job: Job):
    pass
    
  @abstractmethod
  def onAfterJobCompleted(self, job: Job):
    pass
    
  @abstractmethod
  def onAfterJobCanceled(self, job: Job):
    pass
    
  @abstractmethod
  def onAfterJobErrored(self, job: Job):
    pass