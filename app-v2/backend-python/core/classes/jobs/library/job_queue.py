import asyncio
from typing import Literal

from .job import (
  JobId,
  Job, 
  JobContextAbstract,
)
from .job_queue_listener import (
  JobQueueEventListener,
  JobQueueEventPayload,
  JobQueueEventPayloadType_JobQueueStarted,
  JobQueueEventPayloadType_JobQueueStopped,
  JobQueueEventPayloadType_JobEnqueued,
  JobQueueEventPayloadType_JobStarted,
  JobQueueEventPayloadType_JobStepCompleted,
  JobQueueEventPayloadType_JobFinished,
)

class JobQueue:
  """
  Instance (that must be singleton) of JobQueue.  
  **Usage**  
  ```python
  # create instance
  jobQueue = JobQueue()
  
  # register event listener
  def listener(payload: JobQueueEventPayload):
    ...
  jobQueue.addListener(listener)
  
  # after app started (and python event loop started)
  jobQueue.start()
  
  # run job
  jobFactory = JobFactory()
  job = jobFactory.createJob(...)
  jobQueue.queueJob(job=job)
  
  # before app stopped
  jobQueue.stop()
  ```
  """
  def __init__(self) -> None:
    self.queue: asyncio.Queue[Job] = asyncio.Queue()
    self.allJobs: list[Job] = []
    self._taskWorker: asyncio.Task | None = None
    self._eventListeners: set[JobQueueEventListener] = set()
    self._jobsRunningTasks: dict[JobId, asyncio.Task] = {}
  
  # public api
  
  def start(self):
    """Start the job queue worker loop."""
    self._taskWorker = asyncio.create_task(self._workerLoop())
    self._emitEvent(payload=JobQueueEventPayloadType_JobQueueStarted())
  
  def stop(self):
    """Stop the job queue worker loop."""
    if self._taskWorker is not None:
      self._taskWorker.cancel()
      self._taskWorker = None
      self._jobsRunningTasks.clear()
      self._emitEvent(payload=JobQueueEventPayloadType_JobQueueStopped())
      # TODO: _taskWorker is memory-leak safe?
      # TODO: queue should be closed ?
      
  def addListener(self, listener: JobQueueEventListener):
    """Add a listener to the job queue."""
    self._eventListeners.add(listener)
  
  def removeListener(self, listener: JobQueueEventListener):
    """Remove a listener from the job queue."""
    self._eventListeners.discard(listener)
    
  def queueJob(self, job: Job):
    """Enqueue a job to the job queue."""
    self.queue.put_nowait(job)
    self.allJobs.append(job)
    self._emitEvent(payload=JobQueueEventPayloadType_JobEnqueued(job=job))
    
  def cancelJobExecutionByJobId(self, jobId: str):
    """Cancel job execution by job id."""
    jobTask = self._jobsRunningTasks.get(jobId)
    if jobTask is None: 
      return (False, "JOB_NOT_FOUND_IN_RUNNING_TASKS")
    cancelResult = jobTask.cancel()
    if cancelResult: 
      return (True, "JOB_CANCELLED")
    return (False, "JOB_CANCEL_FAILED")
      
  def getAllJobsHistoryAsArrayOfDict(self):
    """Get all jobs history as array of dict."""
    return [job.toDict() for job in self.allJobs]
      
  # internal api
    
  async def _workerLoop(self):
    """Worker loop for the job queue."""
    while True:
      
      # get job + create job context
      job = await self.queue.get()
      jobCtx = JobExecutionContextJobQueue(job=job,jobQueue=self)
      
      # create execution function (ready for asyncio.Task)
      async def execute():
        await job.jobFn(job, jobCtx)
        
      try:
        # job-started
        job.markAsRunning()
        self._emitEvent(payload=JobQueueEventPayloadType_JobStarted(job=job))
        # run job fn
        task = asyncio.create_task(execute())
        self._jobsRunningTasks[job.id] = task
        await task
        # job-finished - completed
        job.markAsCompleted()
        del self._jobsRunningTasks[job.id]
        self._emitEvent(payload=JobQueueEventPayloadType_JobFinished(finishedReason="COMPLETED", job=job))
      except asyncio.CancelledError:
        # job-finished - canceled
        job.markAsCanceled()
        del self._jobsRunningTasks[job.id]
        self._emitEvent(payload=JobQueueEventPayloadType_JobFinished(finishedReason="CANCELED", job=job))
      except Exception as e:
        # job-finished - errored
        job.markAsErrored(e)
        del self._jobsRunningTasks[job.id]
        self._emitEvent(payload=JobQueueEventPayloadType_JobFinished(finishedReason="ERRORED", job=job))
      finally:
        # cleanup
        self.queue.task_done()
        
  def _emitEvent(self,payload: JobQueueEventPayload):
    """Emit an event to all listeners."""
    for listener in self._eventListeners:
      listener(payload)
      # asyncio.create_task(listener(payload))
      
    
    
class JobExecutionContextJobQueue(JobContextAbstract):
  """
  Job execution context injected in Job.jobFn when executed.  
  Used for doing operation on JobQueue from inside jobFn.  
  **IMPORTANT**: This context is coupled with JobQueue.  
  """
  def __init__(
    self, 
    job: Job,
    jobQueue: "JobQueue"
  ):
    self.job: Job = job
    self.jobQueue: "JobQueue" = jobQueue
    
  def triggerJobCancel(self):
    """Raise the exception expected by JobQueue to cancel the Job while executing."""
    job = self.job
    jobQueue = self.jobQueue
    
    jobQueue.cancelJobExecutionByJobId(jobId=job.id)
    
  def incrementStepCompleted(self):
    """Increment the step counter and mark the job as step completed."""
    job = self.job
    jobQueue = self.jobQueue
    
    job.markAsStepCompleted()
    jobQueue._emitEvent(payload=JobQueueEventPayloadType_JobStepCompleted(job=job))
    
  def addMessage(self, kind: Literal["ERROR","INFO"], message: str):
    """Add a message to the job state."""
    job = self.job
    
    job.addMessage(f"{kind}: {message}")
    
    
  