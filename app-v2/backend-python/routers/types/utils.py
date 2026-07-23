from typing import Literal
from pydantic import BaseModel, Field

class UtilsDiskRevealInFinder_RequestBody(BaseModel):
  path: str = Field(title="Path", description="Path to reveal")
   
UtilsDiskRevealInFinder_Response200 = Literal[True]