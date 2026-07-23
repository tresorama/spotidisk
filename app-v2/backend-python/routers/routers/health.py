from fastapi import APIRouter

from ..spec.openapi import OPENAPI_TAG_NAME
from ..types.health import HealthGetStatus_Response200

from core.singleton.logger import loggerHTTP as logger

router = APIRouter(
  prefix="/health", 
  tags=[OPENAPI_TAG_NAME.HEALTH],
)

@router.get("/",
            operation_id="healthGetStatus", 
            summary="Get health status",
            )
async def health_getStatus() -> HealthGetStatus_Response200:
  return HealthGetStatus_Response200(
    status="ok",
    version="2.1.0",
  )