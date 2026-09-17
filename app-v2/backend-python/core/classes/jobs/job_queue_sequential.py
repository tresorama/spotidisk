import asyncio

from core.classes.logger.logger import LoggerFactory
from core.classes.jobs.job_queue import JobQueue
from core.classes.jobs.job import Job
from core.classes.jobs.job_queue_lifecycle_effect import JobQueueLifecycleEffect

class JobQueueSequential(JobQueue):
  """
  Jobs Queue Manager with SEQUENTIAL strategy:  
  - uses a queue (tasks are executed in SEQUENTIAL, only 1 at a time)
  """
  
  def __init__(
    self,
    DELAY_BETWEEN_MONITOR_TICK: float = 5.0,
    DELAY_BETWEEN_WORKER_GET_NEXT_JOB: float = 5.0
  ):
    # init instances
    self.logger = LoggerFactory.create(name="JOB QUEUE")
    self._taskWorker: asyncio.Task | None = None
    self._taskMonitor: asyncio.Task | None = None
    self._jobQueueEffectsDispatcher: JobQueueEffectsDispatcher = JobQueueEffectsDispatcher()
    # save config + deps
    self.DELAY_BETWEEN_MONITOR_TICK = DELAY_BETWEEN_MONITOR_TICK
    self.DELAY_BETWEEN_WORKER_GET_NEXT_JOB = DELAY_BETWEEN_WORKER_GET_NEXT_JOB
    # init data
    self.queueFullList: list[Job] = []
    self.queue: list[Job] = []
    self.endedJobs: list[Job] = []
    self.jobRunning: Job | None = None
    
  # public api
  
  def startQueue(self):
    """
    Initialize internal background jobs (worker and monitor).  
    NOTE: this function must be called after the event loop is started
    """
    self._taskWorker = asyncio.create_task(self._workersLoop())
    self._taskMonitor = asyncio.create_task(self._monitorLoop())
    self._jobQueueEffectsDispatcher.onAfterInit()
    
  async def stopQueue(self):
    """
    Stop internal background jobs (worker and monitor).  
    Usually called before the event loop is closed
    """
    if self._taskWorker:
      self.logger.info('[JobQueue.stopQueue] STOPPING WORKER LOOP...')
      self._taskWorker.cancel()
      resultWorker = await asyncio.gather(
        self._taskWorker,
        return_exceptions=True
      )
      self.logger.info(f'[JobQueue.stopQueue] STOPPED WORKER LOOP - {resultWorker}')
      
    if self._taskMonitor:
      self._taskMonitor.cancel()
      resultMonitor = await asyncio.gather(
        self._taskMonitor,
        return_exceptions=True
      )
      self.logger.info(f'[JobQueue.stopQueue] STOPPED MONITOR LOOP - {resultMonitor}')
    
  def registerLifecycleEffect(self, jobQueueLifecycleEffect:JobQueueLifecycleEffect):
    self._jobQueueEffectsDispatcher.registerLifecycleEffect(jobQueueLifecycleEffect)
    
  async def queueJob(self, job:Job):
    # add job to queue
    self.queueFullList.append(job)
    self.queue.append(job)
    # run lifecycle effect
    self._jobQueueEffectsDispatcher.onAfterJobQueued(job)
    
  # internal

  async def _workersLoop(self):
    self.logger.info('[JobQueue.initWorkers.workerLoop] START')
    while (True):
      # wait
      await asyncio.sleep(self.DELAY_BETWEEN_WORKER_GET_NEXT_JOB)
      # if one job is running, skip
      if self.jobRunning: continue
      # if queue is empty, skip
      if not self.queue: continue
      # get next job
      job = self.queue.pop(0)
      # set job as running
      self.jobRunning = job
      # run job
      job.setCallback_beforeJobStart(self._jobQueueEffectsDispatcher.onBeforeJobStart)
      job.setCallback_afterIncrementStep(self._jobQueueEffectsDispatcher.onAfterIncrementStep)
      job.setCallback_afterJobFinished(self._jobQueueEffectsDispatcher.onAfterJobFinished)
      await job.runJobFn()
      # set job as not running
      self.jobRunning = None
      # add job to ended jobs
      self.endedJobs.append(job)
    
    self._taskWorker = asyncio.create_task(workerLoop())

  async def _monitorLoop(self):
    self.logger.info('[JobQueue.initMonitor.monitorLoop] START')
    while (True):
      await asyncio.sleep(self.DELAY_BETWEEN_MONITOR_TICK)
      jobsInQueueIds = [job.id for job in self.queue]
      jobsInQueueCount = len(jobsInQueueIds)
      jobsEndedIds = [job.id for job in self.endedJobs]
      jobsEndedCount = len(jobsEndedIds)
      jobRunningIds = [self.jobRunning.id] if self.jobRunning else []
      jobsRunningCount = len(jobRunningIds)
      self.logger.debug(f"[MONITOR TICK]\n  - IN_QUEUE: {jobsInQueueCount} {jobsInQueueIds}\n  - RUNNING: {jobsRunningCount} {jobRunningIds}\n  - ENDED: {jobsEndedCount} {jobsEndedIds}")


# internal class

class JobQueueEffectsDispatcher:
  def __init__(self):
    self._jobQueueLifecycleEffects: list[JobQueueLifecycleEffect] = []
    
  def registerLifecycleEffect(self, jobQueueLifecycleEffect:JobQueueLifecycleEffect):
    self._jobQueueLifecycleEffects.append(jobQueueLifecycleEffect)
    
  def onAfterInit(self):
    for jobQueueLifecycleEffect in self._jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterInit()
      
  def onAfterJobQueued(self, job:Job):
    for jobQueueLifecycleEffect in self._jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterJobQueued(job)
  
  def onBeforeJobStart(self, job:Job):
    for jobQueueLifecycleEffect in self._jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onBeforeJobStart(job)

  def onAfterIncrementStep(self, job:Job):
    for jobQueueLifecycleEffect in self._jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterIncrementStep(job)

  def onAfterJobFinished(self, job:Job):
    for jobQueueLifecycleEffect in self._jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterJobFinished(job)

