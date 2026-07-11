import asyncio

from core.classes.logger.logger import LoggerFactory
from core.classes.jobs.job_queue import JobQueue
from core.classes.jobs.job import Job
from core.classes.jobs.job_queue_lifecycle_effect import JobQueueLifecycleEffect
from core.classes.utils.utils_background_job import UtilsBackgroundJob

class JobQueueSequential(JobQueue):
  """
  Jobs Queue Manager with SEQUENTIAL strategy:  
  - uses a queue (task are executed in SEQUENTIAL, only 1 at a time)
  """
  
  def __init__(
    self,
    DELAY_BETWEEN_WORKER_GET_NEXT_JOB: float,
    DELAY_BETWEEN_MONITOR_TICK: float,
  ):
    # save config + deps
    self.DELAY_BETWEEN_WORKER_GET_NEXT_JOB = DELAY_BETWEEN_WORKER_GET_NEXT_JOB
    self.DELAY_BETWEEN_MONITOR_TICK = DELAY_BETWEEN_MONITOR_TICK
    # init instances
    self.logger = LoggerFactory.create(name="JOB QUEUE")
    self.jobIdGenerator = JobIdGenerator()
    self.backgroundJobWorker: UtilsBackgroundJob | None = None
    self.backgroundJobMonitor: UtilsBackgroundJob | None = None
    self.jobQueueLifecycleEffects: list[JobQueueLifecycleEffect] = []
    # init data
    self.queueFullList: list[Job] = []
    self.queue: list[Job] = []
    self.endedJobs: list[Job] = []
    self.jobRunning: Job | None = None
    
  # public api
  
  def init(self):
    """
    Initialize internal background jobs (worker and monitor).  
    NOTE: this function must be called after the event loop is started
    """
    self._initMonitor()
    self._initWorkers()
    self._lifecycle_onAfterInit()
    
  def registerLifecycleEffect(self, jobQueueLifecycleEffect:JobQueueLifecycleEffect):
    self.jobQueueLifecycleEffects.append(jobQueueLifecycleEffect)
    
  async def queueJob(self, job:Job):
    # add id to job
    job.id = str(self.jobIdGenerator.generate())
    # add job to queue
    self.queueFullList.append(job)
    self.queue.append(job)
    # run lifecycle effect
    self._lifecycle_onAfterJobQueued(job)
    
  # internal

  def _initWorkers(self):
    async def workerLoop():
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
        job.setCallback_beforeJobStart(self._lifecycle_onBeforeJobStart)
        job.setCallback_afterIncrementStep(self._lifecycle_onAfterIncrementStep)
        job.setCallback_afterJobCompleted(self._lifecycle_onAfterJobCompleted)
        job.setCallback_afterJobCanceled(self._lifecycle_onAfterJobCanceled)
        job.setCallback_afterJobErrored(self._lifecycle_onAfterJobErrored)
        await job.runJobFn()
        # set job as not running
        self.jobRunning = None
        # add job to ended jobs
        self.endedJobs.append(job)
    
    self.backgroundJobWorker = UtilsBackgroundJob(fn=workerLoop)

  def _initMonitor(self):
    async def monitorLoop():
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
        
    self.backgroundJobMonitor = UtilsBackgroundJob(fn=monitorLoop)

  # internal - lifecycle
  def _lifecycle_onAfterInit(self):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterInit()
      
  def _lifecycle_onAfterJobQueued(self, job:Job):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterJobQueued(job)
  
  def _lifecycle_onBeforeJobStart(self, job:Job):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onBeforeJobStart(job)

  def _lifecycle_onAfterIncrementStep(self, job:Job):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterIncrementStep(job)

  def _lifecycle_onAfterJobCompleted(self, job:Job):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterJobCompleted(job)

  def _lifecycle_onAfterJobCanceled(self, job:Job):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterJobCanceled(job)

  def _lifecycle_onAfterJobErrored(self, job:Job):
    for jobQueueLifecycleEffect in self.jobQueueLifecycleEffects:
      jobQueueLifecycleEffect.onAfterJobErrored(job)



class JobIdGenerator:
  def __init__(self):
    self.id = 0
  def generate(self):
    self.id += 1
    return self.id

