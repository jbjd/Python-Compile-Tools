from unittest.mock import patch

import pytest
from personal_compile_utils.validation import is_root

_is_root_cases: list = [("posix", 0, True), ("posix", 1, False)]


@pytest.mark.parametrize("os_name,return_value,expected_is_root", _is_root_cases)
def test_is_root(os_name: str, return_value: int, expected_is_root: bool):
    with (
        patch("personal_compile_utils.validation.os.name", os_name),
        patch(
            "personal_compile_utils.validation.os.geteuid",
            lambda: return_value,
            create=True,
        ),
    ):
        if expected_is_root:
            assert is_root()
        else:
            assert not is_root()
