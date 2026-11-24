from typing import Literal
from pydantic import BaseModel, Field

from ..spec.errors import HttpExpectedError_500_InternalServerError


class UtilsDiskRevealInFinder_RequestBody(BaseModel):
  path: str = Field(title="Path", description="Path to reveal")
   
class UtilsDiskRevealInFinder_Response200(BaseModel):
  status: Literal["REVEALED", "PATH_NOT_EXISTS"] = Field(title="Result key", description="Outcome of the operation")
  
UtilsDiskRevealInFinder_ResponseError500 = HttpExpectedError_500_InternalServerError