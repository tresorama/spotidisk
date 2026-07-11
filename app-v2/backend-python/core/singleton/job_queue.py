from core.singleton.logger import loggerJobQueue
from core.singleton.websocket_event_emitter import webSocketEventEmitter

from core.classes.jobs.job_queue_sequential import JobQueueSequential
from core.classes.jobs.job_queue_lifecycle_effect_logger import JobQueueLifecycleEffect_Logger
from core.classes.jobs.job_queue_lifecycle_effect_websocket_notifier import JobQueueLifecycleEffect_WebSocketNotifier

# init singletons

# main queue
jobQueue = JobQueueSequential(
  DELAY_BETWEEN_MONITOR_TICK=1,
  DELAY_BETWEEN_WORKER_GET_NEXT_JOB=5,
)

# lifecycle effects
jobQueueLifecycleEffect_logger = JobQueueLifecycleEffect_Logger(
  jobQueue=jobQueue,
  logger=loggerJobQueue,
)
jobQueueLifecycleEffect_webSocketNotifier = JobQueueLifecycleEffect_WebSocketNotifier(
  jobQueue=jobQueue,
  logger=loggerJobQueue,
  webSocketEventEmitter=webSocketEventEmitter,
)
jobQueue.registerLifecycleEffect(jobQueueLifecycleEffect_logger)
jobQueue.registerLifecycleEffect(jobQueueLifecycleEffect_webSocketNotifier)