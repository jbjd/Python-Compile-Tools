"""Tests for the validation module"""

from unittest.mock import patch

import pytest

from personal_compile_tools.validation import is_root, raise_if_not_root

_MODULE_NAME: str = "personal_compile_tools.validation"

_is_root_cases: list = [
    ("posix", 0, True),
    ("posix", 1, False),
    ("nt", 0, False),
    ("nt", 1, True),
]


@pytest.mark.parametrize("os_name,return_value,expected_is_root", _is_root_cases)
def test_is_root(os_name: str, return_value: int, expected_is_root: bool):
    """Should return correct bool given OS native response code."""

    with (
        patch(f"{_MODULE_NAME}.os.name", os_name),
        patch(
            f"{_MODULE_NAME}.os.geteuid",
            lambda: return_value,
            create=True,
        ),
        patch(f"{_MODULE_NAME}.ctypes", create=True),  # Hack for non-windows systems
        patch(
            f"{_MODULE_NAME}.ctypes.windll.shell32.IsUserAnAdmin",
            lambda: return_value,
            create=True,
        ),
    ):
        assert is_root() is expected_is_root


@pytest.mark.parametrize("is_root", (True, False))
def test_raise_if_not_root(is_root: bool):
    """Should raise PermissionsError if not root."""

    error_message: str = "test"

    with patch(f"{_MODULE_NAME}.is_root", return_value=is_root):
        if not is_root:
            with pytest.raises(PermissionError, match=error_message):
                raise_if_not_root(error_message)
        else:
            raise_if_not_root(error_message)
