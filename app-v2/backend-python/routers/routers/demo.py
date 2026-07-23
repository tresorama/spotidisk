from __future__ import annotations
from typing import Literal
from fastapi import APIRouter

from ..spec.openapi import OPENAPI_TAG_NAME
from ..types.demo import DemoJobStart_Response200

from core.singleton.logger import loggerHTTP as logger
from core.singleton.job_queue import jobQueue
from core.classes.jobs.job_demo import JobDemo

router = APIRouter(
  prefix="/demo", 
  tags=[OPENAPI_TAG_NAME.DEMO],
)

@router.post("/job-demo/start", 
             operation_id="demoJobDemoStart", 
             summary="Start demo job"
             )
async def demo_jobDemoStart() -> DemoJobStart_Response200:
  logger.info("/demo/job-demo/start - Starting demo job")
  # create job + schedule job
  job = JobDemo.createJob()
  await jobQueue.queueJob(job)
  # reply
  logger.info("/demo/job-demo/start - Demo job schduled and started")
  logger.info("/demo/job-demo/start - Reply HTTP")
  return True
