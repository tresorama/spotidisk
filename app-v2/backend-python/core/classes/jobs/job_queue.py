from abc import ABC, abstractmethod

from core.classes.jobs.job import Job


class JobQueue(ABC):
  
  queueFullList: list[Job]
  
  @abstractmethod
  def init(self):
    pass
    
  @abstractmethod
  def queueJob(self, job: Job):
    pass
  