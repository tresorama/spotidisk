from __future__ import annotations
from fastapi import APIRouter, HTTPException

from ..spec.openapi import OPENAPI_TAG_NAME
from ..spec.errors import HttpUnexpectedError_CodeShouldBeUnreachable
from ..routers_types.settings import (
  SettingsGetSettings_Response200,
  SettingsUpdateSettings_RequestBody,
  SettingsUpdateSettings_Response200,
  SettingsUpdateSettings_ResponseError500,
)

from core.singleton.logger import loggerHTTP as logger
from core.singleton.service_settings import serviceSettings

router = APIRouter(
  prefix="/settings", 
  tags=[OPENAPI_TAG_NAME.SETTINGS],
)

@router.get("/", 
            operation_id="settingsGetSettings",
            summary="Get settings"
            )
async def getSettings() -> SettingsGetSettings_Response200:
  logger.info("GET SETTINGS")
  
  result = serviceSettings.getSettings()
  
  if result[0] == False:
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  settings = result[2]
  return settings

@router.put("/", 
            operation_id="settingsUpdateSettings",
            summary="Update settings",
            responses={
              500: { "model": SettingsUpdateSettings_ResponseError500 },
            },
            )
async def updateSettings(requestBody: SettingsUpdateSettings_RequestBody) -> SettingsUpdateSettings_Response200:
  logger.info(f"UPDATE SETTINGS, requestBody={requestBody}")
  
  result = serviceSettings.updateSettings(payload=requestBody)
  
  if result[0] == False:
    if result[1] == "DB_UPDATE_ERROR":
      message = f"Error updating settings: {result[2]}"
      logger.error(message)
      raise SettingsUpdateSettings_ResponseError500(message=message).toHttpException()
    message = f"ERROR BRANCH NOT HANDLED. Reason: {result[1]}"
    logger.error(message)
    raise HttpUnexpectedError_CodeShouldBeUnreachable(message=message).toHttpException()
  
  return True