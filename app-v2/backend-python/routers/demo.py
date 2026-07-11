from __future__ import annotations

from fastapi import APIRouter
from core.singleton.logger import loggerHTTP as logger
from core.singleton.job_queue import jobQueue
from core.classes.jobs.job_demo import JobDemo

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/job-demo/start", response_model=bool)
async def jobDemo_start():
  logger.info("/demo/job-demo/start - Starting demo job")
  # create job + schedule job
  job = JobDemo.createJob()
  await jobQueue.queueJob(job)
  # reply
  logger.info("/demo/job-demo/start - Demo job schduled and started")
  logger.info("/demo/job-demo/start - Reply HTTP")
  return True
