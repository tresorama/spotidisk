import sys
import re
from .utils_os import UtilsOS


class TestUtilsOS_getOsType:
  def test_it(self):
    OS_PLATFORM = sys.platform
    result = UtilsOS.getOsType()
    if OS_PLATFORM == "darwin":
      assert result == "MAC_OS"
    elif OS_PLATFORM == "win32":
      assert result == "WINDOWS"
    else:
      assert result == "LINUX"
      
class TestUtilsOS_getUserHomeDirectoryPath:
  def test_it(self):
    os_type = UtilsOS.getOsType()
    result = UtilsOS.getUserHomeDirectoryPath()
    if os_type == "MAC_OS":
      assert re.match(r"^/Users/[^/]+$", result)
    elif os_type == "WINDOWS":
      assert re.match(r"^C:/Users/[^/]+$", result)
    else:
      assert re.match(r"^/home/[^/]+$", result)
      
class TestUtilsOS_getUserAppDataDirectoryPath:
  def test_it(self):
    os_type = UtilsOS.getOsType()
    result = UtilsOS.getUserAppDataDirectoryPath()
    if os_type == "MAC_OS":
      assert re.match(r"^/Users/[^/]+/Library/Application Support$", result)
    elif os_type == "WINDOWS":
      assert re.match(r"^C:/Users/[^/]+/AppData$", result)
    else:
      assert re.match(r"^/home/[^/]+/.config$", result)