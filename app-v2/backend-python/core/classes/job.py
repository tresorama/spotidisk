from typing import Callable, Awaitable

class Job:
  """Job Definition Object"""
  def __init__(
    self, 
    title: str, 
    totalStepCount: int,
    jobFn: Callable[[], Awaitable[None]]
  ):
    self.title = title
    self.stepsTotal = totalStepCount
    self.stepsCurrentNum = 0
    self.jobFn = jobFn
    
  def isRunning(self):
    return self.stepsTotal > self.stepsCurrentNum
  
  def incrementStep(self):
    self.stepsCurrentNum += 1
  
  def getProgress(self):
    if self.isRunning(): return (self.stepsCurrentNum / self.stepsTotal)
    else: return 1
    