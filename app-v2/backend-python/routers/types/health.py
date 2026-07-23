from typing import Literal
from pydantic import BaseModel, Field

class HealthGetStatus_Response200(BaseModel):
  status: Literal["ok"] = Field(title="Status",description="Status of the backend")
  version: str = Field(title="Version",description="Version of the backend")