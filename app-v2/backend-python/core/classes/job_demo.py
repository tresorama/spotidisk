import asyncio
from core.singleton.logger import logger
from core.classes.job import Job
    
class JobDemo:
  def createJob(self):
    logger.info("JobDemo - Creating demo job")
    
    # create job fn
    totalStep = 5
    
    async def jobFn(job:Job):
      logger.info("JobDemo - jobFn - start")
      for i in range(totalStep):
        logger.info(f"JobDemo - jobFn - Job step {i+1}/{totalStep}")
        job.incrementStep()
        await asyncio.sleep(5)
      logger.info(f"JobDemo - jobFn - Job completed")
      
    # create job
    job = Job(
      title="Demo Job",
      totalStepCount=totalStep,
      jobFn=jobFn
    )
    logger.info(f"JobDemo - Job created: {job}")
    
    return job