from typing import Literal

from models.settings import Settings, SettingsMutable

from ..spec.errors import HttpExpectedError_500_InternalServerError

# get 
SettingsGetSettings_Response200 = Settings

# update
SettingsUpdateSettings_RequestBody = SettingsMutable
SettingsUpdateSettings_Response200 = Literal[True]
SettingsUpdateSettings_ResponseError500 = HttpExpectedError_500_InternalServerError
