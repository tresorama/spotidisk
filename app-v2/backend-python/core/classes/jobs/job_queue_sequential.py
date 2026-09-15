import asyncio
from collections import deque

from core.classes.logger.logger import LoggerFactory
from core.classes.jobs.job_queue import JobQueue
from core.classes.jobs.job import Job
from core.classes.jobs.job_queue_lifecycle_effect import JobQueueLifecycleEffect


class JobQueueSequential(JobQueue):
  """Sequential async job queue: only one job runs at a time."""

  MAX_ENDED_JOBS = 100

  def __init__(
    self,
    DELAY_BETWEEN_WORKER_GET_NEXT_JOB: float = 0,
    DELAY_BETWEEN_MONITOR_TICK: float = 1,
  ):
    self.logger = LoggerFactory.create(name="JOB QUEUE")
    self.jobIdGenerator = JobIdGenerator()
    self.workerTask: asyncio.Task | None = None
    self.monitorTask: asyncio.Task | None = None
    self.jobQueueLifecycleEffects: list[JobQueueLifecycleEffect] = []
    self.queueFullList: list[Job] = []
    self.queue: asyncio.Queue[Job] = asyncio.Queue()
    self.endedJobs: deque[Job] = deque(maxlen=self.MAX_ENDED_JOBS)
    self.jobRunning: Job | None = None
    self.DELAY_BETWEEN_WORKER_GET_NEXT_JOB = DELAY_BETWEEN_WORKER_GET_NEXT_JOB
    self.DELAY_BETWEEN_MONITOR_TICK = DELAY_BETWEEN_MONITOR_TICK

  def init(self):
    """Start the worker and monitor after the event loop has started."""
    self.workerTask = asyncio.create_task(self._workerLoop())
    self.monitorTask = asyncio.create_task(self._monitorLoop())
    self._lifecycle_onAfterInit()

  def registerLifecycleEffect(self, jobQueueLifecycleEffect: JobQueueLifecycleEffect):
    self.jobQueueLifecycleEffects.append(jobQueueLifecycleEffect)

  async def queueJob(self, job: Job):
    job.id = str(self.jobIdGenerator.generate())
    self.queueFullList.append(job)
    await self.queue.put(job)
    self._lifecycle_onAfterJobQueued(job)

  async def _workerLoop(self):
    self.logger.info("[JobQueue.worker] START")
    while True:
      job = await self.queue.get()
      self.jobRunning = job
      try:
        job.setCallback_beforeJobStart(self._lifecycle_onBeforeJobStart)
        job.setCallback_afterIncrementStep(self._lifecycle_onAfterIncrementStep)
        job.setCallback_afterJobCompleted(self._lifecycle_onAfterJobCompleted)
        job.setCallback_afterJobCanceled(self._lifecycle_onAfterJobCanceled)
        job.setCallback_afterJobErrored(self._lifecycle_onAfterJobErrored)
        await job.runJobFn()
        self.endedJobs.append(job)
      finally:
        self.jobRunning = None
        self.queue.task_done()

  async def _monitorLoop(self):
    self.logger.info("[JobQueue.monitor] START")
    while True:
      await asyncio.sleep(self.DELAY_BETWEEN_MONITOR_TICK)
      queuedJobs = list(self.queue._queue)
      queuedIds = [job.id for job in queuedJobs]
      runningIds = [self.jobRunning.id] if self.jobRunning else []
      endedIds = [job.id for job in self.endedJobs]
      self.logger.debug(
        f"[MONITOR TICK]\\n"
        f"  - IN_QUEUE: {len(queuedIds)} {queuedIds}\\n"
        f"  - RUNNING: {len(runningIds)} {runningIds}\\n"
        f"  - ENDED: {len(endedIds)} {endedIds}"
      )

  async def cancelRunningJob(self):
    """Request cooperative cancellation of the currently running job."""
    if self.jobRunning:
      self.jobRunning.requestCancellation()

  def _lifecycle_onAfterInit(self):
    for effect in self.jobQueueLifecycleEffects:
      effect.onAfterInit()

  def _lifecycle_onAfterJobQueued(self, job: Job):
    for effect in self.jobQueueLifecycleEffects:
      effect.onAfterJobQueued(job)

  def _lifecycle_onBeforeJobStart(self, job: Job):
    for effect in self.jobQueueLifecycleEffects:
      effect.onBeforeJobStart(job)

  def _lifecycle_onAfterIncrementStep(self, job: Job):
    for effect in self.jobQueueLifecycleEffects:
      effect.onAfterIncrementStep(job)

  def _lifecycle_onAfterJobCompleted(self, job: Job):
    for effect in self.jobQueueLifecycleEffects:
      effect.onAfterJobCompleted(job)

  def _lifecycle_onAfterJobCanceled(self, job: Job):
    for effect in self.jobQueueLifecycleEffects:
      effect.onAfterJobCanceled(job)

  def _lifecycle_onAfterJobErrored(self, job: Job):
    for effect in self.jobQueueLifecycleEffects:
      effect.onAfterJobErrored(job)


class JobIdGenerator:
  def __init__(self):
    self.id = 0

  def generate(self):
    self.id += 1
    return self.id
