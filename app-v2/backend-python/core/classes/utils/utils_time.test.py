import datetime
from time import sleep
import pytest
from .utils_time import UtilsTime, UtilsTimeExecutionTimer


class TestGetCurrentDateTimeIso:
    def test_returns_iso_format_string(self):
        result = UtilsTime.getCurrentDateTimeIso()
        # check that creating a datetime from it is valid
        parsed = datetime.datetime.fromisoformat(result)
        assert isinstance(parsed, datetime.datetime)

    def test_returns_current_time(self, mocker):
        fixed_now = datetime.datetime(2020, 1, 1, 12, 30, 45, 123000)
        mocker.patch("core.classes.utils.utils_time.datetime").datetime.now.return_value = fixed_now
        result = UtilsTime.getCurrentDateTimeIso()
        assert result == fixed_now.isoformat()


class TestFormatDurationInSecondsToMMSS:
    @pytest.mark.parametrize(
      "seconds,expected", 
      [
        (0, "00:00"),
        (5, "00:05"),
        (59, "00:59"),
        (60, "01:00"),
        (61, "01:01"),
        (125, "02:05"),
        (599, "09:59"),
        (600, "10:00"),
        (3600, "60:00"),
        (65.9, "01:05"),  # troncamento, non arrotondamento
      ]
    )
    def test_formats_correctly(self, seconds, expected):
        assert UtilsTime.formatDurationInSecondsToMMSS(seconds) == expected


class TestUtilsTimeExecutionTimer:
    def test_time_elapsed(self, mocker):
        # run timer
        timer = UtilsTimeExecutionTimer()
        sleep(1.0)
        result = timer.end()
        # check
        print(result)
        assert result["fullMs"] == pytest.approx(1000.0, abs=50)
        assert result["str_mmss"] == "00:01"
        assert float(result["str_ss"]) == pytest.approx(1.0, abs=0.05)
        