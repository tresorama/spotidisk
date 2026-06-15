import asyncio
from core.classes.job import Job
from core.singleton.logger import logger

class JobsExecutor:
  """In-Memory Job Executor. Used to execute jobs and share the current job state between threads and python functions"""
  job: None | Job = None
  task: None | asyncio.Task = None
  
  def getCurrentJob(self):
    if not self.job:  return None
    if not self.task: return None
    return (self.job, self.task)
  
  def setAndStartNewJob(self, job: Job):
    # cancel any existing job
    if self.task and not self.task.done():
      logger.info("JobsExecutor - setAndStartNewJob - canceling existing job")
      self.task.cancel()
      self.task.remove_done_callback(self.onTaskDone)
    # set new job
    self.job = job
    # start new job
    self.task = asyncio.create_task(job.jobFn(job))
    # add listeners
    self.task.add_done_callback(self.onTaskDone)
    
  def onTaskDone(self, task: asyncio.Task):
    if self.task == task:
      self.task = None
      self.job = None