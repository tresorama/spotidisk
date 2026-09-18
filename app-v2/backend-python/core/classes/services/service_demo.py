import asyncio
import random

from core.classes.logger.logger import Logger
from core.classes.jobs.lib.job_factory import JobFactory
from core.classes.jobs.lib.job import Job, JobContextAbstract
from core.classes.notifications.websocket_event_emitter import WebSocketEventEmitter
from models.ws import WsBackendEventPayloadTypeMessage

class ServiceDemo:
  def __init__(
    self, 
    logger: Logger,
    webSocketEventEmitter: WebSocketEventEmitter,
    jobFactory: JobFactory,
  ):
    self.logger: Logger = logger
    self.webSocketEventEmitter: WebSocketEventEmitter = webSocketEventEmitter
    self.jobFactory: JobFactory = jobFactory
    
  def createJob(self):
    logger = self.logger
    jobFactory = self.jobFactory
    webSocketEventEmitter = self.webSocketEventEmitter
    
    # create job fn
    totalStep = 3
    async def jobFn(job:Job, ctx: JobContextAbstract):
      # constants
      delay = 2
      
      # functions
      async def doStep():
        # wait
        await asyncio.sleep(delay)
        # return random result
        isError = random.random() > 0.75
        isErrorThatFailJob = random.random() > 0.5
        if isError and isErrorThatFailJob:
          return (False, "UNEXPECTED_ERROR_THAT_FAIL_JOB")
        if isError:
          return (False, "EXPECTED_ERROR_THAT_DOES_NOT_FAIL_JOB")
        return (True, None)
      
      # notify job start
      logger.info("JobDemo - jobFn - start")
      
      # do each step
      for i in range(totalStep):
        
        # notify step start
        logger.info(f"JobDemo - jobFn - Step {i+1}/{totalStep}: doing...")
        await webSocketEventEmitter.emit(eventPayload=WsBackendEventPayloadTypeMessage(text=f"Job \"{job.title}\" step {i+1}/{totalStep}: doing..."))
        
        # do step
        isSuccess, errorCode = await doStep()
        
        # - if error
        if not isSuccess and errorCode == 'UNEXPECTED_ERROR_THAT_FAIL_JOB':
          raise Exception("UNEXPECTED_ERROR_THAT_FAIL_JOB")
        elif not isSuccess and errorCode == 'EXPECTED_ERROR_THAT_DOES_NOT_FAIL_JOB':
          ctx.addMessage(kind="ERROR",message="EXPECTED_ERROR_THAT_DOES_NOT_FAIL_JOB")
        # - if success
        else: 
          ctx.addMessage(kind="INFO",message=f"Step {i+1}/{totalStep} done")
        
        # increment step
        ctx.incrementStepCompleted()
        
        # notify step done
        logger.info(f"JobDemo - jobFn - Step {i+1}/{totalStep}: done!")
        await webSocketEventEmitter.emit(eventPayload=WsBackendEventPayloadTypeMessage(text=f"Job \"{job.title}\" step {i+1}/{totalStep}: done!"))
        
      # after each step done -> notify job done
      logger.info(f"JobDemo - jobFn - Job completed")
      
    # create job
    job = jobFactory.createJob(
      title="Demo Job",
      stepsTotal=totalStep,
      jobFn=jobFn
    )
    logger.info(f"JobDemo - Job created: {job.id}")
    
    return job