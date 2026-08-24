from typing import Literal
from models.settings import Settings, SettingsMutable

SettingsGetSettings_Response200 = Settings

SettingsUpdateSettings_RequestBody = SettingsMutable
SettingsUpdateSettings_Response200 = Literal[True]