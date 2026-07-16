from core.singleton.logger import loggerAppConfig

from core.classes.config.app_config import (
  EnvironmentVariables,
  AppConfigRuntime, 
  AppConfig, 
)

# init singletons

envVars = EnvironmentVariables() # pyright: ignore[reportCallIssue]
appConfigRuntime = AppConfigRuntime(envVars=envVars)

appConfig = AppConfig(
  logger=loggerAppConfig,
  envVars=envVars,
  runtime=appConfigRuntime,
)
