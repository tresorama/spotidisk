from models.ws import (
  WsBackendEventPayloadTypeMessage,
  WsBackendEventPayloadTypeJobProgress
)

from core.classes.logger.logger import Logger
from core.classes.jobs.job import Job
from core.classes.jobs.job_queue import JobQueue
from core.classes.jobs.job_queue_lifecycle_effect import JobQueueLifecycleEffect
from core.classes.notifications.websocket_event_emitter import WebSocketEventEmitter
from core.classes.utils.utils_background_job import UtilsBackgroundJob
from core.classes.utils.utils_time import UtilsTime

class JobQueueLifecycleEffect_WebSocketNotifier(JobQueueLifecycleEffect):
  def __init__(
    self,
    jobQueue: JobQueue,
    logger: Logger,
    webSocketEventEmitter: WebSocketEventEmitter,
  ):
    self.jobQueue = jobQueue
    self.logger = logger
    self.webSocketEventEmitter = webSocketEventEmitter
    
  def onAfterInit(self):
    self.logger.info(f"onInit - Job Queue started")
    self._notifyJobProgress()
  
  def onAfterJobQueued(self, job: Job):
    self._notifyJobQueued(job)
    self._notifyJobProgress()
  
  def onBeforeJobStart(self,job: Job):
    self._notifyJobStarted(job)
    self._notifyJobProgress()
    
  def onAfterIncrementStep(self,job: Job):
    self._notifyJobProgress()
    
  def onAfterJobCompleted(self, job: Job):
    self._notifyJobCompleted(job)
    self._notifyJobProgress()

  def onAfterJobCanceled(self, job: Job):
    self._notifyJobCanceled(job)
    self._notifyJobProgress()
    
  def onAfterJobErrored(self, job: Job):
    self._notifyJobErrored(job)
    self._notifyJobProgress()
    
  # notifications
  
  def _notifyJobQueued(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" queued",
        )
      )
    )
    
  def _notifyJobStarted(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" started",
        )
      )
    )
  
  def _notifyJobCompleted(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" completed",
          severity="SUCCESS"
        )
      )
    )
  
  def _notifyJobCanceled(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" canceled",
          severity="WARNING"
        )
      )
    )
  
  def _notifyJobErrored(self, job: Job):
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeMessage(
          text=f"Job \"{job.title}\" errored.\nERROR\n{job.error}",
          severity="ERROR"
        )
      )
    )
  
  def _notifyJobProgress(self):
    # get status of queue
    allJobs = self.jobQueue.queueFullList
    
    UtilsBackgroundJob(
      fn=self.webSocketEventEmitter.emit(
        eventPayload=WsBackendEventPayloadTypeJobProgress(
          dateTimeISO=UtilsTime.getCurrentDateTimeIso(),
          jobs=[
            {
              "id": job.id or '-',
              "title": job.title,
              "executionStatus": job.getExecutionStatus(),
              "stepsTotal": job.stepsTotal,
              "stepsCompleted": job.stepsCompleted or 0,
              "progress": job.getProgress(),
              "messages": job.messages,
            }
            for job in allJobs
          ]
        )
      )
    )
