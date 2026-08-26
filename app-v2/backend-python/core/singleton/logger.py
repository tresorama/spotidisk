from core.classes.logger.logger import LoggerFactory

loggerAppConfig = LoggerFactory.create(name="APP CONFIG")
loggerUserConfigApi = LoggerFactory.create(name="USER CONFIG API")
loggerJobQueue = LoggerFactory.create(name="JOB QUEUE")
loggerNativeDepsChecker = LoggerFactory.create(name="NATIVE DEPS CHECKER")
loggerWSActiveConnections = LoggerFactory.create(name="WS ACTIVE CONNECTIONS")
loggerWSEventEmitter = LoggerFactory.create(name="WS EVENT EMITTER")

loggerSpotifyApi = LoggerFactory.create(name="SPOTIFY API")
loggerYoutubeApi = LoggerFactory.create(name="YOUTUBE API")
loggerMetadata = LoggerFactory.create(name="METADATA")
loggerOperations = LoggerFactory.create(name="OPERATIONS")

loggerServicePlaylist = LoggerFactory.create(name="SERVICE PLAYLIST")
loggerServiceSettings = LoggerFactory.create(name="SERVICE SETTINGS")

loggerHTTP = LoggerFactory.create(name="HTTP API")
loggerWS = LoggerFactory.create(name="WS API")