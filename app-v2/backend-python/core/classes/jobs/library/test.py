import asyncio
import pytest

from .job_factory import JobFactory
from .job_queue import JobQueue, JobQueueEventPayload
from .job import Job, JobContextAbstract

class TestsJobQueueStartAndStop:
  @pytest.mark.asyncio
  async def test_job_queue_can_start_stop_and_restart(self):
    # init singletons
    jobQueue = JobQueue()

    # track events
    eventsPayloads: list[JobQueueEventPayload] = []
    def listener(payload: JobQueueEventPayload) -> None:
      eventsPayloads.append(payload)
      
    # add listener
    jobQueue.addListener(listener)
    
    # start
    jobQueue.start()
    assert jobQueue._taskWorker is not None
    assert eventsPayloads[-1].kind == "JOB-QUEUE-STARTED"
    
    # stop
    jobQueue.stop()
    assert jobQueue._taskWorker is None
    assert eventsPayloads[-1].kind == "JOB-QUEUE-STOPPED"
    
    # restart
    jobQueue.start()
    assert jobQueue._taskWorker is not None
    assert eventsPayloads[-1].kind == "JOB-QUEUE-STARTED"
    
    # stop
    jobQueue.stop()
    assert jobQueue._taskWorker is None
    assert eventsPayloads[-1].kind == "JOB-QUEUE-STOPPED"
    
    # remove listener
    jobQueue.removeListener(listener)
    
  @pytest.mark.asyncio
  async def test_job_queue_listeners_can_be_added_and_removed(self):
    # init singletons
    jobQueue = JobQueue()
    
    # define listener
    def listener(payload: JobQueueEventPayload) -> None:
      pass
    
    # add listener
    jobQueue.addListener(listener)
    assert len(jobQueue._eventListeners) == 1
    
    # remove listener
    jobQueue.removeListener(listener)
    assert len(jobQueue._eventListeners) == 0
    

class TestsJobs:
  @pytest.mark.asyncio
  async def test_job_state_during_execution_job_success(self):
    # init singletons
    jobFactory = JobFactory()
    jobQueue = JobQueue()
    jobQueue.start()
    
    # create job
    jobTitle = "J S"
    jobStepsTotal = 3
    async def jobFn(job: Job, ctx: JobContextAbstract):
      for i in range(1, job.stepsTotal+1):
        ctx.incrementStepCompleted()
    job = jobFactory.createJob(title=jobTitle, stepsTotal=jobStepsTotal, jobFn=jobFn)
    jobId = job.id
    
    # check inside events
    def listener(payload: JobQueueEventPayload):
      if (payload.kind == "JOB-QUEUED"):
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.status == "WAITING_START"
        assert payload.job.progress == 0
        assert payload.job.stepsCompleted == None
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is None
        assert payload.job.finished_at is None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "WAITING_START"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is None
        assert stateDict["finished_at"] is None
      if (payload.kind == "JOB-STARTED"):
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == 0
        assert payload.job.status == "RUNNING"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is not None
        assert payload.job.finished_at is None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "RUNNING"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is not None
        assert stateDict["finished_at"] is None
      if (payload.kind == "JOB-FINISHED"):
        assert payload.finishedReason == "COMPLETED"
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == jobStepsTotal
        assert payload.job.status == "COMPLETED"
        assert payload.job.progress == 1
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is not None
        assert payload.job.finished_at is not None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "COMPLETED"
        assert stateDict["progress"] == 1.0
        assert stateDict["stepsCompleted"] == jobStepsTotal
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is not None
        assert stateDict["finished_at"] is not None
    
    # enqueue job
    jobQueue.addListener(listener)
    jobQueue.queueJob(job=job)
    
    # cleanup
    jobQueue.removeListener(listener)
    
  @pytest.mark.asyncio
  async def test_job_state_during_execution_job_errored(self):
    # init singletons
    jobFactory = JobFactory()
    jobQueue = JobQueue()
    jobQueue.start()
    
    # create job
    jobTitle = "J E"
    jobStepsTotal = 3
    async def jobFn(job: Job, ctx: JobContextAbstract):
      raise Exception("error")
    job = jobFactory.createJob(title=jobTitle, stepsTotal=jobStepsTotal, jobFn=jobFn)
    jobId = job.id
    
    # check inside events
    def listener(payload: JobQueueEventPayload):
      if (payload.kind == "JOB-QUEUED"):
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == None
        assert payload.job.status == "WAITING_START"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is None
        assert payload.job.finished_at is None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "WAITING_START"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is None
        assert stateDict["finished_at"] is None
      if (payload.kind == "JOB-STARTED"):
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == 0
        assert payload.job.status == "RUNNING"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is not None
        assert payload.job.finished_at is None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "RUNNING"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is not None
        assert stateDict["finished_at"] is None
      if (payload.kind == "JOB-FINISHED"):
        assert payload.finishedReason == "ERRORED"
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == 0
        assert payload.job.status == "ERRORED"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == True
        assert payload.job.error is not None
        assert isinstance(payload.job.error, Exception)
        assert payload.job.started_at is not None
        assert payload.job.finished_at is not None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "ERRORED"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is not None
        assert stateDict["started_at"] is not None
        assert stateDict["finished_at"] is not None
    
    # enqueue job
    jobQueue.addListener(listener)
    jobQueue.queueJob(job=job)
    
    # cleanup
    jobQueue.removeListener(listener)
    
  @pytest.mark.asyncio
  async def test_job_state_during_execution_job_canceled(self):
    # init singletons
    jobFactory = JobFactory()
    jobQueue = JobQueue()
    jobQueue.start()
    
    # create job
    jobTitle = "J E"
    jobStepsTotal = 3
    async def jobFn(job: Job, ctx: JobContextAbstract):
      ctx.triggerJobCancel()
    job = jobFactory.createJob(title=jobTitle, stepsTotal=jobStepsTotal, jobFn=jobFn)
    jobId = job.id
    
    # check inside events
    def listener(payload: JobQueueEventPayload):
      if (payload.kind == "JOB-QUEUED"):
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == None
        assert payload.job.status == "WAITING_START"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is None
        assert payload.job.finished_at is None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "WAITING_START"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is None
        assert stateDict["finished_at"] is None
      if (payload.kind == "JOB-STARTED"):
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == 0
        assert payload.job.status == "RUNNING"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == False
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is not None
        assert payload.job.finished_at is None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "RUNNING"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is not None
        assert stateDict["finished_at"] is None
      if (payload.kind == "JOB-FINISHED"):
        assert payload.finishedReason == "CANCELED"
        # state
        assert payload.job.id == jobId
        assert payload.job.title == jobTitle
        assert payload.job.stepsTotal == jobStepsTotal
        assert payload.job.stepsCompleted == 0
        assert payload.job.status == "CANCELED"
        assert payload.job.progress == 0
        assert payload.job.isCanceled == True
        assert payload.job.isErrored == False
        assert payload.job.error is None
        assert payload.job.started_at is not None
        assert payload.job.finished_at is not None
        # state dict
        stateDict = payload.job.toDict()
        assert stateDict["id"] == jobId
        assert stateDict["title"] == jobTitle
        assert stateDict["stepsTotal"] == jobStepsTotal
        assert stateDict["status"] == "CANCELED"
        assert stateDict["progress"] == 0.0
        assert stateDict["stepsCompleted"] == 0
        assert stateDict["messages"] == []
        assert stateDict["error"] is None
        assert stateDict["started_at"] is not None
        assert stateDict["finished_at"] is not None
    
    # enqueue job
    jobQueue.addListener(listener)
    jobQueue.queueJob(job=job)
    
    # cleanup
    jobQueue.removeListener(listener)
  
  @pytest.mark.asyncio
  async def test_job_status_of_multiple_jobs(self):
    # init singletons
    jobFactory = JobFactory()
    jobQueue = JobQueue()
    jobQueue.start()
    
    # create jobs
    async def jobSuccessFn(job: Job, ctx: JobContextAbstract):
      await asyncio.sleep(1)
      ctx.incrementStepCompleted()
    jobSuccess = jobFactory.createJob(title="JOB-SUCCESS",stepsTotal=1,jobFn=jobSuccessFn)
    
    async def jobErrorFn(job: Job, ctx: JobContextAbstract): 
      await asyncio.sleep(1)
      raise Exception("error")
    jobError = jobFactory.createJob(title="JOB-ERROR",stepsTotal=1,jobFn=jobErrorFn)
    
    async def jobCancelFn(job: Job, ctx: JobContextAbstract):
      await asyncio.sleep(1)
      ctx.triggerJobCancel()
    jobCancel = jobFactory.createJob(title="JOB-CANCEL",stepsTotal=1,jobFn=jobCancelFn)
    
    # enqueue jobs
    jobQueue.queueJob(job=jobSuccess)
    jobQueue.queueJob(job=jobError)
    jobQueue.queueJob(job=jobCancel)
    
    # wait for jobs to finish
    await asyncio.sleep(4)
    
    # check status of jobs
    assert jobSuccess.status == "COMPLETED"
    assert jobSuccess.started_at is not None
    assert jobSuccess.finished_at is not None
    assert jobSuccess.progress == 1.0
    assert jobSuccess.stepsCompleted == 1
    
    assert jobError.status == "ERRORED"
    assert jobError.started_at is not None
    assert jobError.finished_at is not None
    assert jobError.progress == 0.0
    assert jobError.stepsCompleted == 0
    
    assert jobCancel.status == "CANCELED"
    assert jobCancel.started_at is not None
    assert jobCancel.finished_at is not None
    assert jobCancel.progress == 0.0
    assert jobError.stepsCompleted == 0
    
    # check state of jobs history
    jobsHistory = jobQueue.getAllJobsHistoryAsArrayOfDict()
    assert len(jobsHistory) == 3
    assert jobsHistory[0]["id"] == jobSuccess.id
    assert jobsHistory[1]["id"] == jobError.id
    assert jobsHistory[2]["id"] == jobCancel.id
    