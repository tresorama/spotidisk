import asyncio
from core.singleton.logger import logger
from core.classes.job import Job
    
class JobDemo:
  def createJob(self):
    logger.info("JobDemo - Creating demo job")
    
    # create job fn
    totalStep = 5
    
    async def jobFn():
      logger.info("JobDemo - jobFn - start")
      logger.info("JobDemo - jobFn - Getting job state...")
      for i in range(totalStep):
        logger.info(f"JobDemo - jobFn - Job step {i+1}/{totalStep}")
        # do something
        job.incrementStep()
        await asyncio.sleep(5)
      logger.info(f"JobDemo - jobFn - Job completed")
      
    # create job state
    job = Job(
      title="Demo Job",
      totalStepCount=totalStep,
      jobFn=jobFn
    )
    logger.info(f"JobDemo - Job state created: {job}")
    
    return job