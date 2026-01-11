"""Tests for the modules module."""

from unittest.mock import MagicMock, patch

from personal_compile_tools.modules import get_module_file_path

_MODULE_NAME: str = "personal_compile_tools.modules"


def test_get_module_file_path():
    """Should return file path to module."""

    file_path: str = "test"

    mock_module = MagicMock()
    mock_module.__file__ = file_path

    with patch(f"{_MODULE_NAME}.import_module", lambda _: mock_module):
        assert get_module_file_path("some_module") == file_path
