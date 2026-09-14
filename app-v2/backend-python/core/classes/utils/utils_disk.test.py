# core/classes/utils/utils_disk.test.py
import os
from pathlib import Path
import pytest
from pytest_mock import MockerFixture
from .utils_disk import UtilsDisk


class TestBuildFilePath:
    def test_joins_dir_and_filename(self):
        assert UtilsDisk.buildFilePath("/tmp/dir", "file.txt") == os.path.join("/tmp/dir", "file.txt")

    def test_handles_trailing_slash_in_dir(self):
        assert UtilsDisk.buildFilePath("/tmp/dir/", "file.txt") == os.path.join("/tmp/dir", "file.txt")


class TestRevealInFinder:
    def test_calls_open_on_mac(self, mocker: MockerFixture):
        mocker.patch(
            "core.classes.utils.utils_disk.UtilsOS.getOsType",
            return_value="MAC_OS",
        )
        run_mock = mocker.patch("core.classes.utils.utils_disk.subprocess.run")
        UtilsDisk.revealInFinder("/some/path")
        args = run_mock.call_args[0][0]
        assert args == ["open", "-R", str(Path("/some/path"))]

    def test_calls_explorer_on_windows(self, mocker: MockerFixture):
        mocker.patch(
            "core.classes.utils.utils_disk.UtilsOS.getOsType",
            return_value="WINDOWS",
        )
        run_mock = mocker.patch("core.classes.utils.utils_disk.subprocess.run")
        UtilsDisk.revealInFinder("/some/path")
        args = run_mock.call_args[0][0]
        assert args == ["explorer", "/select,", str(Path("/some/path"))]

    def test_calls_xdg_open_on_linux(self, mocker: MockerFixture):
        mocker.patch(
            "core.classes.utils.utils_disk.UtilsOS.getOsType",
            return_value="LINUX",
        )
        run_mock = mocker.patch("core.classes.utils.utils_disk.subprocess.run")
        UtilsDisk.revealInFinder("/some/dir/file.txt")
        args = run_mock.call_args[0][0]
        assert args == ["xdg-open", str(Path("/some/dir"))]


class TestCheckIfFileExists:
    def test_true_when_exists(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("content")
        assert UtilsDisk.checkIfFileExists(str(f)) is True

    def test_false_when_missing(self, tmp_path: Path):
        assert UtilsDisk.checkIfFileExists(str(tmp_path / "missing.txt")) is False

class TestCheckIfDirExists:
    def test_true_when_exists(self, tmp_path: Path):
        assert UtilsDisk.checkIfDirExists(str(tmp_path)) is True

    def test_false_when_missing(self, tmp_path: Path):
        assert UtilsDisk.checkIfDirExists(str(tmp_path / "nope")) is False

class TestCheckIfFolderIsWritable:
    def test_writable_dir(self, tmp_path: Path):
        assert UtilsDisk.checkIfFolderIsWritable(str(tmp_path)) is True

    def test_missing_dir_returns_false(self, tmp_path: Path):
        assert UtilsDisk.checkIfFolderIsWritable(str(tmp_path / "nope")) is False


class TestDeriveDirPathFromFilePath:
    def test_returns_parent_dir(self):
        assert UtilsDisk.deriveDirPathFromFilePath("/a/b/file.txt") == str(Path("/a/b"))

    def test_relative_path(self):
        assert UtilsDisk.deriveDirPathFromFilePath("dir/file.txt") == str(Path("dir"))

    def test_no_parent(self):
        assert UtilsDisk.deriveDirPathFromFilePath("file.txt") == str(Path("."))


class TestCreateDirIfNotExists:
    def test_creates_nested_dirs(self, tmp_path: Path):
        target = tmp_path / "a" / "b" / "c"
        UtilsDisk.createDirIfNotExists(str(target))
        assert target.exists()

    def test_idempotent_if_already_exists(self, tmp_path: Path):
        UtilsDisk.createDirIfNotExists(str(tmp_path))  # non deve sollevare eccezioni
        assert tmp_path.exists()


class TestDeleteFileIfExists:
    def test_deletes_existing_file(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        UtilsDisk.deleteFileIfExists(str(f))
        assert not f.exists()

    def test_noop_if_missing(self, tmp_path: Path):
        UtilsDisk.deleteFileIfExists(str(tmp_path / "missing.txt"))  # non deve fallire


class TestDeleteFile:
    def test_returns_file_not_found(self, tmp_path: Path):
        result = UtilsDisk.deleteFile(str(tmp_path / "missing.txt"))
        assert result == "FILE_NOT_FOUND"

    def test_returns_success(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        result = UtilsDisk.deleteFile(str(f))
        assert result == "SUCCESS"
        assert not f.exists()

    def test_returns_delete_error(self, tmp_path: Path, mocker: MockerFixture):
        f = tmp_path / "file.txt"
        f.write_text("x")
        mocker.patch(
            "core.classes.utils.utils_disk.Path.unlink",
            side_effect=Exception("boom"),
        )
        result = UtilsDisk.deleteFile(str(f))
        assert result == "FILE_DELETE_ERROR"


class TestMoveFileOrDirectory:
    def test_success(self, tmp_path: Path):
        old = tmp_path / "old.txt"
        old.write_text("x")
        new = tmp_path / "new.txt"
        assert UtilsDisk.moveFileOrDirectory(str(old), str(new)) is True
        assert new.exists() and not old.exists()

    def test_failure_returns_false(self, mocker: MockerFixture):
        mocker.patch(
            "core.classes.utils.utils_disk.os.rename",
            side_effect=OSError("boom"),
        )
        assert UtilsDisk.moveFileOrDirectory("a", "b") is False


class TestGetDirectoryFilesNames:
    def test_lists_only_files(self, tmp_path: Path):
        (tmp_path / "file1.txt").write_text("x")
        (tmp_path / "file2.txt").write_text("x")
        (tmp_path / "subdir").mkdir()
        names = UtilsDisk.getDirectoryFilesNames(str(tmp_path))
        assert sorted(names) == ["file1.txt", "file2.txt"]

    def test_empty_list_if_dir_missing(self, tmp_path: Path):
        assert UtilsDisk.getDirectoryFilesNames(str(tmp_path / "nope")) == []

    def test_empty_dir(self, tmp_path: Path):
        assert UtilsDisk.getDirectoryFilesNames(str(tmp_path)) == []


class TestMakeExecutable:
    def test_sets_permissions(self, tmp_path: Path):
        # create file
        f = tmp_path / "file"
        f.write_text("x")
        # get permissions before
        wasExecutable = os.access(f, os.X_OK)  # True se eseguibile (per l'utente corrente)
        assert wasExecutable is False
        # make executable
        UtilsDisk.makeExecutable(str(f))
        # get permissions after
        isExecutable = os.access(f, os.X_OK)  # True se eseguibile (per l'utente corrente)
        assert isExecutable is True


class TestSanitizeNameForFileOrDirectoryNameUse:
    @pytest.mark.parametrize("raw,expected", [
        ("valid_name", "valid_name"),
        ("bad/name", "badname"),
        ("bad\\name", "badname"),
        ("name:with:colons", "namewithcolons"),
        ("wild*card?", "wildcard"),
        ('quoted"name"', "quotedname"),
        ("<tag>", "tag"),
        ("pipe|name", "pipename"),
        ("it's a name", "its a name"),
        ('all/\\:*?"<>|\'chars', "allchars"),
        ("", ""),
        ("no special chars", "no special chars"),
    ])
    def test_removes_invalid_chars(self, raw, expected):
        assert UtilsDisk.sanitizeNameForFileOrDirectoryNameUse(raw) == expected