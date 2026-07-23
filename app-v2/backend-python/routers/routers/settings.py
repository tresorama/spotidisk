from __future__ import annotations
from fastapi import APIRouter, HTTPException

from ..spec.openapi import OPENAPI_TAG_NAME
from ..types.settings import (
  SettingsGetSettings_Response200,
  SettingsUpdateSettings_RequestBody,
  SettingsUpdateSettings_Response200,
)

from core.singleton.user_config_api import userConfigReaderApi

router = APIRouter(
  prefix="/settings", 
  tags=[OPENAPI_TAG_NAME.SETTINGS],
)

@router.get("/", 
            operation_id="settingsGetSettings",
            summary="Get settings"
            )
async def getSettings() -> SettingsGetSettings_Response200:
  return userConfigReaderApi.getSettings()

@router.put("/", 
            operation_id="settingsUpdateSettings",
            summary="Update settings",
            )
async def updateSettings(settingsMutable: SettingsUpdateSettings_RequestBody) -> SettingsUpdateSettings_Response200:
  updated = userConfigReaderApi.updateSettings(
    newSettingsMutable=settingsMutable
  )
  if not updated:
    raise HTTPException(status_code=500, detail="Failed to update settings")
  return True