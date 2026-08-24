from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .openapi_types import (
  OpenApiGeneralMetadata,
  OpenApiTagDef,
  OPENAPI_TAG_NAME,
)
from .errors import HttpExpectedError_500_InternalServerError

# constants

# openapi tags
OPENAPI_TAGS: dict[OPENAPI_TAG_NAME, OpenApiTagDef] = {
  OPENAPI_TAG_NAME.API_DOCS: {
    "name": OPENAPI_TAG_NAME.API_DOCS,
    "description": "Endpoints for OpenAPI documentation UIs"
  },
  OPENAPI_TAG_NAME.HOME: {
    "name": OPENAPI_TAG_NAME.HOME,
    "description": "Endpoints for base api info"
  },
  OPENAPI_TAG_NAME.HEALTH: {
    "name": OPENAPI_TAG_NAME.HEALTH,
    "description": "Endpoints for health checks of the backend"
  },
  OPENAPI_TAG_NAME.DEMO: {
    "name": OPENAPI_TAG_NAME.DEMO,
    "description": "Endpoints for demo features (developer debugging)"
  },
  OPENAPI_TAG_NAME.WS: {
    "name": OPENAPI_TAG_NAME.WS,
    "description": "Endpoints for WebSockets Features"
  },
  OPENAPI_TAG_NAME.PLAYLIST: {
    "name": OPENAPI_TAG_NAME.PLAYLIST,
    "description": "Endpoints for consuming User Playlists"
  },
  OPENAPI_TAG_NAME.SETTINGS: {
    "name": OPENAPI_TAG_NAME.SETTINGS,
    "description": "Endpoints for consuming User Settings"
  },
  OPENAPI_TAG_NAME.UTILS: {
    "name": OPENAPI_TAG_NAME.UTILS,
    "description": "Endpoints for consuming Backend Utilities. (e.g. disk reveal in finder)"
  },
} 

# openapi metadata
OPENAPI_METADATA: OpenApiGeneralMetadata = {
  "title": "SpotiDisk API",
  "summary": "Spotify Playlist Downloader (audio source YouTube)",
  "description":"Backend API for SpotiDisk, an app to download Spotify Playlists as audio source from YouTube.",
  "version":"1.0.0",
}

def createFastApiOpenApiExtender(app: FastAPI):
  """
  Factory of function that will extend the FastApi OpenAPI Schema:
  - add 500 HTTP Error to components/schemas
  - add 500 HTTP Error to responses of every route (that doesn't have it already)
  """
  def fastApiOpenApiExtender():
    # Se lo schema è già stato calcolato, restituisci quello in cache
    if app.openapi_schema:
        return app.openapi_schema

    # Genera lo schema base di FastAPI
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    
    # 1. Registra lo schema Pydantic sotto components/schemas
    # Assicuriamo che il dizionario 'components' e 'schemas' esistano
    components = openapi_schema.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    schemas[HttpExpectedError_500_InternalServerError.__name__] = HttpExpectedError_500_InternalServerError.model_json_schema()

    # 2. Definisci il blocco di risposta 500 standard
    responses_500 = {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": f"#/components/schemas/{HttpExpectedError_500_InternalServerError.__name__}"
                }
            }
        },
    }

    # 3. Cicla su tutte le route e inietta la risposta 500
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
          if not 500 in method.setdefault("responses", {}):
              # Inietta la 500 in ogni metodo (GET, POST, PUT, DELETE, ecc.)
              method.setdefault("responses", {})["500"] = responses_500

    app.openapi_schema = openapi_schema
    return app.openapi_schema
  
  return fastApiOpenApiExtender
