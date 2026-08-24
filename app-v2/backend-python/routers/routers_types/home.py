from pydantic import BaseModel, Field

class HomeGetSystemInfo_Response200(BaseModel):
  app: str = Field(title="App",description="Name of the app")
  version: str = Field(title="Version",description="Version of the app")