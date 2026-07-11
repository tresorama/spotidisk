from core.classes.logger.logger import Logger
from core.classes.jobs.job import Job
from core.classes.jobs.job_queue import JobQueue
from core.classes.jobs.job_queue_lifecycle_effect import JobQueueLifecycleEffect

class JobQueueLifecycleEffect_Logger(JobQueueLifecycleEffect):
  def __init__(
    self, 
    jobQueue:JobQueue,
    logger:Logger,
  ):
    self.jobQueue = jobQueue
    self.logger = logger
    
  def onAfterInit(self):
    self.logger.info(f"onInit - Job Queue started")
    
  def onAfterJobQueued(self, job: Job):
    self.logger.info(f"onAfterJobQueued - Job {job.title} queued")
  
  def onBeforeJobStart(self, job: Job):
    self.logger.info(f"onBeforeJobStart - Job {job.title} started")
    
  def onAfterIncrementStep(self, job: Job):
    self.logger.info(f"onAfterIncrementStep - Job {job.title} step {job.stepsCompleted}/{job.stepsTotal} completed")
    
  def onAfterJobCompleted(self, job: Job):
    self.logger.info(f"onAfterJobDone - Job {job.title} completed")
    
  def onAfterJobCanceled(self, job: Job):
    self.logger.info(f"onAfterJobCanceled - Job {job.title} canceled")
    
  def onAfterJobErrored(self, job: Job):
    self.logger.info(f"onAfterJobErrored - Job {job.title} errored")