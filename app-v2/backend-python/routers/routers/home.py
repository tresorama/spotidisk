from fastapi import APIRouter

from ..spec.openapi import OPENAPI_TAG_NAME
from ..routers_types.home import HomeGetSystemInfo_Response200

router = APIRouter(
  tags=[OPENAPI_TAG_NAME.HOME],
)

@router.get("/", 
            operation_id="homeGetSystemInfo", 
            summary="Get system/backend info"
            )
async def health_getSystemInfo() -> HomeGetSystemInfo_Response200:
  return HomeGetSystemInfo_Response200(
    app="SpotiDisk Backend",
    version="2.1.0",
  )