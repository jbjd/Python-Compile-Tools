from unittest.mock import MagicMock, patch

import pytest

from personal_compile_tools.validation import is_root

_MODULE_NAME: str = "personal_compile_tools.validation"

_is_root_cases: list = [
    ("posix", 0, True),
    ("posix", 1, False),
    ("nt", 0, False),
    ("nt", 1, True),
]


@pytest.mark.parametrize("os_name,return_value,expected_is_root", _is_root_cases)
def test_is_root(os_name: str, return_value: int, expected_is_root: bool):
    """Should return correct bool given OS native response code"""
    ctypes = MagicMock()
    ctypes.windll = MagicMock()
    ctypes.windll.shell32 = MagicMock()
    ctypes.windll.shell32.IsUserAnAdmin = MagicMock()
    ctypes.windll.shell32.IsUserAnAdmin.return_value = return_value

    with (
        patch(f"{_MODULE_NAME}.os.name", os_name),
        patch(
            f"{_MODULE_NAME}.os.geteuid",
            lambda: return_value,
            create=True,
        ),
        patch(f"{_MODULE_NAME}.ctypes", ctypes, create=True),
    ):
        if expected_is_root:
            assert is_root()
        else:
            assert not is_root()
