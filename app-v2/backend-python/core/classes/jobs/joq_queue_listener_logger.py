from .library.job_queue import JobQueue, JobQueueEventPayload

from core.classes.logger.logger import Logger

class JobQueueListener_Logger():
  def __init__(
    self, 
    logger: Logger,
    jobQueue: JobQueue,
  ):
    self.logger = logger
    self.jobQueue = jobQueue
    
  def listener(self, payload: JobQueueEventPayload):
    
    if (payload.kind == "JOB-QUEUE-STARTED"):
      self.logger.info(f"JOB-QUEUE-STARTED")
      self.printQueueCounts()
      return
    
    if (payload.kind == "JOB-QUEUE-STOPPED"):
      self.logger.info(f"JOB-QUEUE-STOPPED")
      self.printQueueCounts()
      return
    
    if (payload.kind == "JOB-QUEUED"):
      job = payload.job
      self.logger.info(f"JOB-QUEUED - Job #{job.id} '{job.title}' queued")
      self.printQueueCounts()
      return
    
    if (payload.kind == "JOB-STARTED"):
      job = payload.job
      self.logger.info(f"JOB-STARTED - Job #{job.id} '{job.title}' started")
      self.printQueueCounts()
      return
    
    if (payload.kind == "JOB-STEP-COMPLETED"):
      job = payload.job
      self.logger.info(f"JOB-STEP-COMPLETED - Job #{job.id} '{job.title}' step {job.stepsCompleted}/{job.stepsTotal} completed")
      return
    
    if (payload.kind == "JOB-FINISHED"):
      self.printQueueCounts()
      
      job = payload.job
      reason = payload.finishedReason
      
      if (reason == "CANCELED"):
        self.logger.info(f"JOB-FINISHED - Job #{job.id} '{job.title}' canceled")
        return
      if (reason == "ERRORED"):
        self.logger.info(f"JOB-FINISHED - Job #{job.id} '{job.title}' errored")
        return
      if (reason == "COMPLETED"):
        self.logger.info(f"JOB-FINISHED - Job #{job.id} '{job.title}' completed")
        return
      
      raise Exception(f"Unknown job finished reason: {reason}")
      
      
  def printQueueCounts(self):
    jobsHistory = self.jobQueue.getAllJobsHistoryAsArrayOfDict()
    
    jobsWaitingIds = [job["id"] for job in jobsHistory if job["status"] == "WAITING"]
    jobsRunningIds = [job["id"] for job in jobsHistory if job["status"] == "RUNNING"]
    jobsCanceledIds = [job["id"] for job in jobsHistory if job["status"] == "CANCELED"]
    jobsErroredIds = [job["id"] for job in jobsHistory if job["status"] == "ERRORED"]
    jobsCompletedIds = [job["id"] for job in jobsHistory if job["status"] == "COMPLETED"]
    
    countAll = len(jobsHistory)
    countWaiting = len(jobsWaitingIds)
    countRunning = len(jobsRunningIds)
    countCanceled = len(jobsCanceledIds)
    countErrored = len(jobsErroredIds)
    countCompleted = len(jobsCompletedIds)
    countFinished = countCanceled + countErrored + countCompleted
    
    message = "[JOB QUEUE MONITOR TICK]"
    message += f"\n- ALL: {countAll}"
    message += f"\n- WAITING: {countWaiting}"
    message += f"\n- RUNNING: {countRunning}"
    message += f"\n- FINISHED: {countFinished} ({countCanceled} canceled, {countErrored} errored, {countCompleted} completed)"
    self.logger.debug(message)
