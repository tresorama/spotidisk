import asyncio
import random
from models.new import WsBackendEventPayloadTypeMessage
from core.singleton.logger import logger
from core.singleton.websocket_event_emitter import webSocketEventEmitter
from core.classes.jobs.job import Job
    
class JobDemo:
  def createJob(self):
    logger.info("JobDemo - Creating demo job")
    
    # create job fn
    totalStep = 3
    
    def maybeRaiseException():
      if random.random() > 0.75:
        raise Exception("Fake exception")
    
    async def jobFn(job:Job):
      # constants
      delay = 2
      # notify job start
      logger.info("JobDemo - jobFn - start")
      # do each step
      for i in range(totalStep):
        # notify step start
        logger.info(f"JobDemo - jobFn - Step {i+1}/{totalStep}: doing...")
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(
            text=f"Job \"{job.title}\" step {i+1}/{totalStep}: doing..."
          )
        )
        # do step
        await asyncio.sleep(delay)
        maybeRaiseException()
        await job.incrementStepCompleted()
        # notify step done
        logger.info(f"JobDemo - jobFn - Step {i+1}/{totalStep}: done!")
        await webSocketEventEmitter.emit(
          eventPayload=WsBackendEventPayloadTypeMessage(
            text=f"Job \"{job.title}\" step {i+1}/{totalStep}: done!"
          )
        )
      # after each step done -> notify job done
      logger.info(f"JobDemo - jobFn - Job completed")
      
    # create job
    job = Job(
      title="Demo Job",
      totalStepCount=totalStep,
      jobFn=jobFn
    )
    logger.info(f"JobDemo - Job created: {job}")
    
    return job