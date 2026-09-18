import asyncio
import pytest
from .utils_background_job import UtilsBackgroundJob

class FakeFn:
  def __init__(
    self,
    initialCallState: int = 0,
    delayInSeconds: int = 0
  ):
    self.calls = initialCallState
    self.DELAY = delayInSeconds
  def getState(self):
    return self.calls
  class FakeError(Exception):
    pass
  async def runError(self):
    raise self.FakeError()
  async def runSuccess(self):
    await asyncio.sleep(self.DELAY)
    self.calls += 1

class TestUtilsBackgroundJob:
    @pytest.mark.asyncio
    async def test_fn_that_raise_an_exception(self):
        FN_TIME = 1
        TEST_TIME = FN_TIME * 1.1
        
        fakeFn = FakeFn(delayInSeconds=FN_TIME)
        job = UtilsBackgroundJob(fn=fakeFn.runError)
        
        # init checks state
        checks = {
          "before": False,
          "after": False,
        }
          
        # define checks
        def checkBeforeJob():
          assert fakeFn.getState() == 0
          assert job.status == "WAITING"
          checks["before"] = True
            
        def checkAfterJob():
          assert fakeFn.getState() == 0
          assert job.status == "DONE_ERROR"
          assert job.error is not None
          assert isinstance(job.error, FakeFn.FakeError)
          checks["after"] = True
        
        # run
        job.setCallback_onComplete(checkAfterJob)
        
        checkBeforeJob()
        job.run()
        await asyncio.sleep(TEST_TIME)
        
        assert checks["before"] is True
        assert checks["after"] is True
        
    @pytest.mark.asyncio
    async def test_fn_that_is_ok(self):
        FN_TIME = 1
        TEST_TIME = FN_TIME * 1.1
      
        fakeFn = FakeFn(delayInSeconds=FN_TIME)
        job = UtilsBackgroundJob(fn=fakeFn.runSuccess)
        
        # init checks state
        checks = {
          "before": False,
          "after": False,
        }
        
        # define checks
        def onBeforeJob():
          assert fakeFn.getState() == 0
          assert job.status == "WAITING"
          checks["before"] = True
        def onComplete():
          assert fakeFn.getState() == 1
          assert job.status == "DONE_OK"
          assert job.error is None
          checks["after"] = True
        
        # run
        job.setCallback_onComplete(onComplete)
        
        onBeforeJob()
        job.run()
        await asyncio.sleep(TEST_TIME)
        
        assert checks["before"] is True
        assert checks["after"] is True
        
    @pytest.mark.asyncio
    async def test_second_fn_can_start_if_other_is_running(self):
        FN1_TIME = 2
        FN2_TIME = 5
        TEST_TIME = max(FN1_TIME, FN2_TIME) * 1.1
        
        fakeFn1 = FakeFn(delayInSeconds=FN1_TIME)
        fakeFn2 = FakeFn(delayInSeconds=FN2_TIME)
        job1 = UtilsBackgroundJob(fn=fakeFn1.runSuccess)
        job2 = UtilsBackgroundJob(fn=fakeFn2.runSuccess)
        
        # define checks
        checks = {
          "before": False,
          "after_1": False,
          "after_2": False,
        }
        
        def checkBefore():
          assert job1.status == "WAITING"
          assert job2.status == "WAITING"
          checks["before"] = True
        def checkAfterJob1():
          assert job1.status == "DONE_OK"
          assert job2.status == "RUNNING"
          checks["after_1"] = True
        def checkAfterJob2():
          assert job1.status == "DONE_OK"
          assert job2.status == "DONE_OK"
          checks["after_2"] = True
        
        # run
        job1.setCallback_onComplete(checkAfterJob1)
        job2.setCallback_onComplete(checkAfterJob2)
        
        checkBefore()
        job1.run()
        job2.run()
        await asyncio.sleep(TEST_TIME)
        
        assert checks["before"] is True
        assert checks["after_1"] is True
        assert checks["after_2"] is True
        
        