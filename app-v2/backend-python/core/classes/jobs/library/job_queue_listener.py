from typing import Annotated, Callable, Literal
from pydantic import BaseModel, ConfigDict, Field

from .job import Job

# types - event 

class JobQueueEventPayloadType_JobQueueStarted(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  kind: Literal["JOB-QUEUE-STARTED"] = "JOB-QUEUE-STARTED"

class JobQueueEventPayloadType_JobQueueStopped(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  kind: Literal["JOB-QUEUE-STOPPED"] = "JOB-QUEUE-STOPPED"

class JobQueueEventPayloadType_JobEnqueued(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  kind: Literal["JOB-QUEUED"] = "JOB-QUEUED"
  job: Job

class JobQueueEventPayloadType_JobStarted(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  kind: Literal["JOB-STARTED"] = "JOB-STARTED"
  job: Job

class JobQueueEventPayloadType_JobStepCompleted(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  kind: Literal["JOB-STEP-COMPLETED"] = "JOB-STEP-COMPLETED"
  job: Job
  
class JobQueueEventPayloadType_JobFinished(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  kind: Literal["JOB-FINISHED"] = "JOB-FINISHED"
  finishedReason: Literal["COMPLETED", "CANCELED", "ERRORED"]
  job: Job


JobQueueEventPayload = Annotated[
  JobQueueEventPayloadType_JobQueueStarted
  | JobQueueEventPayloadType_JobQueueStopped
  | JobQueueEventPayloadType_JobEnqueued
  | JobQueueEventPayloadType_JobStarted
  | JobQueueEventPayloadType_JobStepCompleted
  | JobQueueEventPayloadType_JobFinished
  ,
  Field(discriminator="kind"),
]

# types -  event listener fn

# JobQueueEventListener = Callable[ [JobQueueEventPayload], Coroutine[Any, Any, None] ]
JobQueueEventListener = Callable[[JobQueueEventPayload], None]
  