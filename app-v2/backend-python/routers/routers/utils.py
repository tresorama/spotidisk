from fastapi import APIRouter

from ..spec.openapi import OPENAPI_TAG_NAME
from ..types.utils import (
  UtilsDiskRevealInFinder_RequestBody,
  UtilsDiskRevealInFinder_Response200,
)

from core.singleton.logger import loggerHTTP as logger

from core.classes.utils.utils_disk import UtilsDisk

router = APIRouter(
  prefix="/utils",
  tags=[OPENAPI_TAG_NAME.UTILS],
)

@router.post("/disk/reveal-in-finder",
             operation_id="utilsDiskRevealInFinder",
             summary="Reveal directory/file in finder",
             )
async def disk_revealInFinder(payload: UtilsDiskRevealInFinder_RequestBody) -> UtilsDiskRevealInFinder_Response200:
  UtilsDisk.revealInFinder(dirOrFilePath=payload.path)
  return True
