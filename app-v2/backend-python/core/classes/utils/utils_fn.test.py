import pytest
from .utils_fn import UtilsFn

class TestRetryFn:
    def test_fn_succeeds_at_first_try(self, mocker):
        fn = mocker.Mock(
          side_effect=[42]
        )
        result = UtilsFn.retryFn(fn)
        assert result == 42
        assert fn.call_count == 1

    def test_fn_succeeds_after_some_failures(self, mocker):
        fn = mocker.Mock(
          side_effect=[
            ValueError("boom"), 
            ValueError("boom"), 
            "ok"
          ]
        )
        result = UtilsFn.retryFn(fn, maxRetries=3)
        assert result == "ok"
        assert fn.call_count == 3

    def test_fn_raises_after_max_retries_reached(self, mocker):
        fn = mocker.Mock(
          side_effect=[
            ValueError("boom1"),
            ValueError("boom2"),
            ValueError("boom3"),
          ]
        )
        with pytest.raises(ValueError, match="boom3"):
            UtilsFn.retryFn(fn, maxRetries=3)
        assert fn.call_count == 3

    def test_fn_raises_if_max_retries_reached(self, mocker):
        fn = mocker.Mock(
          side_effect=[
            ValueError("boom1"),
            ValueError("boom2"),
            ValueError("boom3"),
          ]
        )
        with pytest.raises(ValueError, match="boom2"):
            UtilsFn.retryFn(fn, maxRetries=2)
        assert fn.call_count == 2