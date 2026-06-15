import time
from core.singleton.logger import logger
from core.singleton.job_state_memory import jobStateMemory
from core.classes.job_state_memory import JobState

    
class JobDemo:
  def createJobState(self):
    logger.info("JobDemo - Creating demo job")
    
    # create job fn
    totalStep = 5
    
    async def jobFn():
      logger.info("JobDemo - jobFn - start")
      logger.info("JobDemo - jobFn - Getting job state...")
      jobState = jobStateMemory.getJobState()
      if not jobState:
        logger.info("JobDemo - jobFn - No job state found")
        raise Exception("JobDemo - jobFn - No job state found")
      for i in range(totalStep):
        logger.info(f"JobDemo - jobFn - Job step {i+1}/{totalStep}")
        # do something
        jobState.incrementStep()
        time.sleep(5)
      logger.info(f"JobDemo - jobFn - Job completed")
      
    # create job state
    jobState = JobState(
      title="Demo Job",
      totalStepCount=totalStep,
      jobFn=jobFn
    )
    logger.info(f"JobDemo - Job state created: {jobState}")
    
    return jobState