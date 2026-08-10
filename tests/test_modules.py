"""Tests for the modules module."""

from typing import Any
from unittest.mock import MagicMock, patch

from personal_compile_tools.modules import (
    can_import_module,
    get_missing_modules,
    get_module_file_path,
    module_is_one_file,
    read_pyproject_file,
)

_MODULE_NAME: str = "personal_compile_tools.modules"


def test_read_pyproject_file():
    """Should return pyproject data as dict."""

    project: dict[str, Any] = read_pyproject_file()

    assert project["project"]["name"] == "personal-compile-tools"


def test_can_import_module():
    """Should determine if a module can be imported."""

    assert can_import_module("os.path")
    assert can_import_module("sys")
    assert not can_import_module("sys.this does not exist")


def test_get_missing_modules():
    """Should return modules that can't be imported."""

    assert get_missing_modules(["os.path", "sys"]) == []

    missing_module: str = "sys. this does not exist"
    assert get_missing_modules(["os.path", missing_module]) == [missing_module]


def test_get_module_file_path():
    """Should return file path to module."""

    file_path: str = "test"

    mock_module = MagicMock()
    mock_module.__file__ = file_path

    with patch(f"{_MODULE_NAME}.import_module", lambda _: mock_module):
        assert get_module_file_path("some_module") == file_path


def test_module_is_one_file():
    """Should return file path to module."""

    mock_module = MagicMock()

    with patch(f"{_MODULE_NAME}.import_module", lambda _: mock_module):
        assert module_is_one_file("some_module") is True

        mock_module.__path__ = "a"

        assert module_is_one_file("some_module") is False
