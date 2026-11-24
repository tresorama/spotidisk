from fastapi import APIRouter

from ..spec.openapi import OPENAPI_TAG_NAME
from ..routers_types.utils import (
  UtilsDiskRevealInFinder_RequestBody,
  UtilsDiskRevealInFinder_Response200,
  UtilsDiskRevealInFinder_ResponseError500,
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
             responses={
               500: { "model": UtilsDiskRevealInFinder_ResponseError500 },
             }
             )
async def disk_revealInFinder(
  payload: UtilsDiskRevealInFinder_RequestBody
) -> UtilsDiskRevealInFinder_Response200:
  # if path not exits -> 200 + PATH NOT EXISTS
  pathExists = UtilsDisk.checkIfDirExists(dirPath=payload.path) | UtilsDisk.checkIfFileExists(filePath=payload.path)
  if not pathExists:
    return UtilsDiskRevealInFinder_Response200(status="PATH_NOT_EXISTS")
  # try to reveal
  success: bool = False
  try:
    UtilsDisk.revealInFinder(dirOrFilePath=payload.path)
    success = True
  except:
    success = False
  # if error -> 500
  if not success:
    raise UtilsDiskRevealInFinder_ResponseError500(message="Cannot reveal fil/folder. Unknonw Error").toHttpException()
  # if succes -> 200
  return UtilsDiskRevealInFinder_Response200(status="REVEALED")
  
