from enum import Enum
from typing import TypedDict

# tags

class OPENAPI_TAG_NAME(Enum):
  """OpenApi Tags Names (Enums)"""
  API_DOCS = "api-docs"
  HOME = "home"
  HEALTH = "health"
  DEMO = "demo"
  WS = "ws"
  PLAYLIST = "playlist"
  SETTINGS = "settings"
  UTILS = "utils"
  
class OpenApiTagDef(TypedDict):
  """OpenApi Tag Definition, that will be exposed as OpenAPI tag definitions"""
  name: OPENAPI_TAG_NAME
  description: str
  
# general
  
class OpenApiGeneralMetadata(TypedDict):
  """OpenApi General Metadata (APi name, description, version...)"""
  title: str
  summary: str
  description: str
  version: str
