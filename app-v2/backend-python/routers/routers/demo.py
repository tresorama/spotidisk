from __future__ import annotations
from fastapi import APIRouter

from ..spec.openapi import OPENAPI_TAG_NAME
from ..routers_types.demo import DemoJobStart_Response200

from core.singleton.logger import loggerHTTP as logger
from core.singleton.jobs import jobQueue
from core.singleton.service_demo import serviceDemo

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
  job = serviceDemo.createJob()
  jobQueue.queueJob(job)
  # reply
  logger.info("/demo/job-demo/start - Demo job schduled and started")
  logger.info("/demo/job-demo/start - Reply HTTP")
  return True
