import asyncio
from core.classes.job_state import JobState

class JobStateMemory:
  """In-Memory Job State Persistence. Used to share job state between threads and python functions"""
  jobState: None | JobState = None
  
  def getJobState(self):
    return self.jobState
  
  def setJobState(self, jobState: JobState):
    self.jobState = jobState
  
  def startJobFn(self):
    jobState = self.jobState
    if not jobState:
      raise Exception("No job state found")
    asyncio.create_task(jobState.jobFn())