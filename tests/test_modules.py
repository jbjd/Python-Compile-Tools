"""Tests for the modules module."""

from typing import Any
from unittest.mock import MagicMock, patch

from personal_compile_tools.modules import (
    get_module_file_path,
    module_is_one_file,
    read_pyproject_file,
)

_MODULE_NAME: str = "personal_compile_tools.modules"


def test_read_pyproject_file():
    """Should return file path to module."""

    project: dict[str, Any] = read_pyproject_file()

    assert project["project"]["name"] == "personal-compile-tools"


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
