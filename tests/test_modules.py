from personal_compile_tools.modules import get_module_file_path
from unittest.mock import MagicMock, patch

_MODULE_NAME: str = "personal_compile_tools.modules"


def test_get_module_file_path():
    file_path: str = "test"

    mock_module = MagicMock()
    mock_module.__file__ = file_path

    with patch(f"{_MODULE_NAME}.import_module", lambda _: mock_module):
        assert get_module_file_path("some_module") == file_path
