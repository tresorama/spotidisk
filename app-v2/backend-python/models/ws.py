from typing import Literal,  Union
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class FrontendQueryKeys: 
  PLAYLIST_ALL = ['playlists']
  @staticmethod
  def PLAYLIST_DETAILS(playlist_id: str): return ['playlists', playlist_id]


class WsBackendEventPayloadTypeMessage(BaseModel):
  kind: Literal["MESSAGE"] = Field(default="MESSAGE", title="Kind", description="Discriminator of the payload")
  text: str = Field(title="Text", description="Text of the message")
  severity: Literal[
    "INFO",
    "WARNING",
    "ERROR",
    "SUCCESS",
  ] = Field(default="INFO", title="Severity", description="Severity of the message")

class WsBackendEventPayloadTypeFrontendQueryInvalidation(BaseModel):
  kind: Literal["FRONTEND_QUERY_INVALIDATION"] = Field(default="FRONTEND_QUERY_INVALIDATION", title="Kind", description="Discriminator of the payload")
  queryKeys: list[str] = Field(title="Query keys", description="List of query keys to invalidate in the frontend (react query keys)", examples=[FrontendQueryKeys.PLAYLIST_ALL])
  
class WsBackendEventPayloadTypeJobProgressJobItem(TypedDict):
  id: str
  title: str
  executionStatus: Literal[
    "WAITING_START",
    "RUNNING",
    "COMPLETED",
    "CANCELED",
    "ERRORED",
  ]
  progress: float
  stepsTotal: int
  stepsCompleted: int
  messages: list[str]
    
class WsBackendEventPayloadTypeJobProgress(BaseModel):
  kind: Literal["JOB_PROGRESS"] = Field(default="JOB_PROGRESS", title="Kind", description="Discriminator of the payload")
  dateTimeISO: str = Field(title="Date time in ISO", description="Date time in ISO. When the backend checked the jobs status.", examples=["2022-01-01T00:00:00.000Z"])
  jobs: list[WsBackendEventPayloadTypeJobProgressJobItem] = Field(title="Jobs", description="List of jobs with progress information")
  
WsBackendEventPayload = Union[
  WsBackendEventPayloadTypeMessage, 
  WsBackendEventPayloadTypeFrontendQueryInvalidation,
  WsBackendEventPayloadTypeJobProgress,
]

class WsBackendEvent(BaseModel):
  dateTimeISO: str = Field(title="Date time in ISO", description="Date time in ISO. When the backend sent the event.", examples=["2022-01-01T00:00:00.000Z"])
  payload: WsBackendEventPayload = Field(discriminator="kind", title="Payload", description="Payload of the event")
