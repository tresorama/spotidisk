from typing import Awaitable, Callable
from .job import Job

class JobFactory:
  """Classes used to create Job. This class is needed to issue job.id"""
  def __init__(self):
    self.jobIdGenerator = JobIdGenerator()
    
  def createJob(
    self, 
    title: str, 
    totalStepCount: int,
    jobFn: Callable[["Job"], Awaitable[None]]
  ):
    job = Job(
      id=str(self.jobIdGenerator.generate()),
      title=title,
      totalStepCount=totalStepCount,
      jobFn=jobFn
    )
    return job
    
    
    
# sub classes

class JobIdGenerator:
  def __init__(self):
    self.id = 0
  def generate(self):
    self.id += 1
    return self.id