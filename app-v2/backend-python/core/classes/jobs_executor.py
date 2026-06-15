import asyncio
from core.classes.job import Job

class JobsExecutor:
  """In-Memory Job Executor. Used to execute jobs and share the current job state between threads and python functions"""
  job: None | Job = None
  task: None | asyncio.Task = None
  
  def getCurrentJob(self):
    if not self.job:
      return None
    if not self.task:
      return None
    return (self.job, self.task)
  
  def setAndStartNewJob(self, job: Job):
    # cancel any existing job
    if self.task and not self.task.done():
      self.task.cancel()
    # set new job
    self.job = job
    # start new job
    self.task = asyncio.create_task(job.jobFn(job))
