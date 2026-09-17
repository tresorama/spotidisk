import asyncio
import pytest

from .job import Job
from .job_factory import JobFactory
from .job_queue_sequential import JobQueueSequential
from .job_queue_lifecycle_effect import JobQueueLifecycleEffect


# classes created for this test file

class JobQueueLifecycleEffectForTest(JobQueueLifecycleEffect):
  def onAfterInit(self):
    print("onAfterInit")
  def onAfterJobQueued(self, job: Job):
    print("onAfterJobQueued", job.getStateAsDict())
  def onBeforeJobStart(self, job: Job):
    print("onBeforeJobStart", job.getStateAsDict())
  def onAfterIncrementStep(self, job: Job):
    print("onAfterIncrementStep", job.getStateAsDict())
  def onAfterJobFinished(self, job: Job):
    print("onAfterJobFinished", job.getExecutionStatus(), job.getStateAsDict())


class State:
  def __init__(self):
    self.count = 0
  def increment(self):
    self.count = self.count + 1
  def getCount(self):
    return self.count
  
class JobFactoryForTest:
  def __init__(
    self,
    jobFactory: JobFactory
  ) -> None:
    self.jobFactory = jobFactory
    
  def createJobSuccess(self):
    state = State()
    stepsCount = 3
    async def jobFn(job: Job):
      for i in range(1, stepsCount+1):
        state.increment()
        message = f"new count: {state.getCount()}" 
        await job.captureMessage(kind="INFO",message=message)
        await job.incrementStepCompleted()
        
    job = self.jobFactory.createJob(
      title="JOB-SUCCESS",
      totalStepCount=stepsCount,
      jobFn=jobFn,
    )
    expectedStateCount = stepsCount
    return (job, state, expectedStateCount)
  
  def createJobErrorManuallyTriggered(self):
    state = State()
    stepsCount = 3
    async def jobFn(job: Job):
      job.triggerError("JOB FAKE ERROR - MANUALLY TRIGGERED")
    job =  self.jobFactory.createJob(
      title="JOB-ERROR-MANUALLY-TRIGGERED",
      totalStepCount=stepsCount,
      jobFn=jobFn,
    )
    expectedStateCount = 0
    return (job, state, expectedStateCount)
  
  def createJobErrorNaturallyRaisedFromCode(self):
    state = State()
    stepsCount = 3
    async def jobFn(job: Job):
      raise Exception("JOB FAK ERROR NATURALLY RAISED FROM CODE")
    job =  self.jobFactory.createJob(
      title="JOB-ERROR-NATURALLY-RAISED-FROM-CODE",
      totalStepCount=stepsCount,
      jobFn=jobFn,
    )
    expectedStateCount = 0
    return (job, state, expectedStateCount)
  
  def createJobCancel(self):
    state = State()
    stepsCount = 3
    async def jobFn(job: Job):
      for i in range(1, stepsCount+1):
        if (i == 1):
          state.increment()
          message = f"new count: {state.getCount()}" 
          await job.captureMessage(kind="INFO",message=message)
          await job.incrementStepCompleted()
          continue
        if (i == 2): 
          job.triggerCancel()
          continue
        state.increment()

    job =  self.jobFactory.createJob(
      title="JOB-CANCEL",
      totalStepCount=stepsCount,
      jobFn=jobFn,
    )
    expectedStateCount = 1
    return (job, state, expectedStateCount)

# create job queue in global scope
jobFactoryForTest = JobFactoryForTest(
  jobFactory=JobFactory()
)
jobQueue = JobQueueSequential(
  DELAY_BETWEEN_MONITOR_TICK=0.1,
  DELAY_BETWEEN_WORKER_GET_NEXT_JOB=0.1
)
jobQueue.registerLifecycleEffect(
  jobQueueLifecycleEffect=JobQueueLifecycleEffectForTest()
)

# test
class TestJobQueueSequential:
  @pytest.mark.asyncio
  async def test_job_queue_is_correctly_started(self):
    jobQueue.startQueue()
    
    assert jobQueue._taskWorker is not None
    if jobQueue._taskWorker is not None:
      assert jobQueue._taskWorker.done() is False
    
    assert jobQueue._taskMonitor is not None
    if jobQueue._taskMonitor is not None:
      assert jobQueue._taskMonitor.done() is False
    
  @pytest.mark.asyncio
  async def test_single_job_success(self):
    job, state, expectedStateCount = jobFactoryForTest.createJobSuccess()
    # run job
    await jobQueue.queueJob(job=job)
    await asyncio.sleep(2)
    assert job.getExecutionStatus() == "COMPLETED"
    assert state.getCount() == expectedStateCount
    
  @pytest.mark.asyncio
  async def test_single_job_error_manually_triggered(self):
    job, state, expectedStateCount = jobFactoryForTest.createJobErrorManuallyTriggered()
    # run job
    await jobQueue.queueJob(job=job)
    await asyncio.sleep(2)
    assert job.getExecutionStatus() == "ERRORED"
    assert job.error is not None
    assert state.getCount() == expectedStateCount
  
  @pytest.mark.asyncio
  async def test_single_job_error_naturally_raised_from_code(self):
    job, state, expectedStateCount = jobFactoryForTest.createJobErrorNaturallyRaisedFromCode()
    # run job
    await jobQueue.queueJob(job=job)
    await asyncio.sleep(2)
    assert job.getExecutionStatus() == "ERRORED"
    assert job.error is not None
    assert state.getCount() == expectedStateCount
    
  @pytest.mark.asyncio
  async def test_single_job_cancel(self):
    job, state, expectedStateCount = jobFactoryForTest.createJobCancel()
    # run job
    await jobQueue.queueJob(job=job)
    await asyncio.sleep(2)
    assert job.getExecutionStatus() == "CANCELED"
    assert state.getCount() == expectedStateCount
    
  @pytest.mark.asyncio
  async def test_multi_job_success(self):
    job1, state1, expectedStateCount1 = jobFactoryForTest.createJobSuccess()
    job2, state2, expectedStateCount2 = jobFactoryForTest.createJobSuccess()
    job3, state3, expectedStateCount3 = jobFactoryForTest.createJobSuccess()
    # run job
    await jobQueue.queueJob(job=job1)
    await jobQueue.queueJob(job=job2)
    await jobQueue.queueJob(job=job3)
    await asyncio.sleep(6)
    assert job1.getExecutionStatus() == "COMPLETED"
    assert job2.getExecutionStatus() == "COMPLETED"
    assert job3.getExecutionStatus() == "COMPLETED"
    assert state1.getCount() == expectedStateCount1
    assert state2.getCount() == expectedStateCount2
    assert state3.getCount() == expectedStateCount3
    
    