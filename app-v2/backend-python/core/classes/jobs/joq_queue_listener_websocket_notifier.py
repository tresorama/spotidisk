from .library.job_queue import JobQueue, JobQueueEventPayload
from .library.job import Job

from models.ws import WsBackendEventPayloadTypeJobProgress,WsBackendEventPayloadTypeMessage
from core.classes.logger.logger import Logger
from core.classes.notifications.websocket_event_emitter import WebSocketEventEmitter
from core.classes.utils.utils_background_job import UtilsBackgroundJob
from core.classes.utils.utils_time import UtilsTime

class JobQueueListener_WebSocketNotifier():
  def __init__(
    self, 
    logger: Logger,
    jobQueue: JobQueue,
    webSocketEventEmitter: WebSocketEventEmitter,
  ):
    self.logger = logger
    self.jobQueue = jobQueue
    self.webSocketEventEmitter = webSocketEventEmitter
    
  def listener(self, payload: JobQueueEventPayload):
    
    if (payload.kind == "JOB-QUEUE-STARTED"):
      self._notifyJobProgress()
      return
    
    if (payload.kind == "JOB-QUEUE-STOPPED"):
      self.logger.info(f"onStop - Job Queue stopped")
      return
    
    if (payload.kind == "JOB-QUEUED"):
      job = payload.job
      self._notifyJobQueued(job)
      self._notifyJobProgress()
      return
    
    if (payload.kind == "JOB-STARTED"):
      job = payload.job
      self._notifyJobStarted(job)
      self._notifyJobProgress()
      return
    
    if (payload.kind == "JOB-STEP-COMPLETED"):
      self._notifyJobProgress()
      return
    
    if (payload.kind == "JOB-FINISHED"):
      job = payload.job
      reason = payload.finishedReason
      
      if (reason == "CANCELED"):
        self._notifyJobCanceled(job)
        self._notifyJobProgress()
        return
      if (reason == "ERRORED"):
        self._notifyJobErrored(job)
        self._notifyJobProgress()
        return
      if (reason == "COMPLETED"):
        self._notifyJobCompleted(job)
        self._notifyJobProgress()
        return
      
      raise Exception(f"Unknown job finished reason: {reason}")
    
    
  # 
  # notifications
  
  def _notifyJobQueued(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" queued",
        )
      )
    ).run()
    
  def _notifyJobStarted(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" started",
        )
      )
    ).run()
  
  def _notifyJobCompleted(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" completed",
          severity="SUCCESS"
        )
      )
    ).run()
  
  def _notifyJobCanceled(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" canceled",
          severity="WARNING"
        )
      )
    ).run()
  
  def _notifyJobErrored(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" errored.\nERROR\n{job.error}",
          severity="ERROR"
        )
      )
    ).run()
  
  def _notifyJobProgress(self):
    # get status of queue
    allJobs = self.jobQueue.allJobs
    
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeJobProgress(
          dateTimeISO=UtilsTime.getCurrentDateTimeIso(),
          jobs=[
            {
              "id": job.id or '-',
              "title": job.title,
              "executionStatus": job.status,
              "stepsTotal": job.stepsTotal,
              "stepsCompleted": job.stepsCompleted or 0,
              "progress": job.progress,
              "messages": job.messages,
            }
            for job in allJobs
          ]
        )
      )
    ).run()