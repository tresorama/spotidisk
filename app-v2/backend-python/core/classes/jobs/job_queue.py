from abc import ABC, abstractmethod

from core.classes.jobs.job import Job


class JobQueue(ABC):
  
  queueFullList: list[Job]
  
  @abstractmethod
  def startQueue(self):
    pass
  
  @abstractmethod
  async def stopQueue(self):
    pass
    
  @abstractmethod
  def queueJob(self, job: Job):
    pass
  
  @abstractmethod
  def getJobById(self, jobId: str) -> Job | None:
    pass
  