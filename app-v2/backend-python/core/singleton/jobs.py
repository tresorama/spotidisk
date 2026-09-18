from core.classes.jobs.lib.job_factory import JobFactory
from core.classes.jobs.lib.job_queue import JobQueue

from core.classes.jobs.joq_queue_listener_logger import JobQueueListener_Logger
from core.classes.jobs.joq_queue_listener_websocket_notifier import JobQueueListener_WebSocketNotifier

from core.singleton.logger import loggerJobQueue
from core.singleton.websocket_event_emitter import webSocketEventEmitter

# init job factory

jobFactory = JobFactory()

# init job queue

jobQueue = JobQueue()
jobQueueEventListener_logger = JobQueueListener_Logger(
  logger=loggerJobQueue,
  jobQueue=jobQueue,
)
jobQueueEventListener_webSocketNotifier = JobQueueListener_WebSocketNotifier(
  logger=loggerJobQueue,
  jobQueue=jobQueue,
  webSocketEventEmitter=webSocketEventEmitter,
)
jobQueue.addListener(jobQueueEventListener_logger.listener)
jobQueue.addListener(jobQueueEventListener_webSocketNotifier.listener)