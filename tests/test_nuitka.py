"""Tests for the nuitka module."""

import pytest

from personal_compile_tools.converters import version_str_to_tuple

try:
    from nuitka import PythonVersions

    from personal_compile_tools.nuitka_ext import (
        nuitka_not_yet_supports_python_version,
        nuitka_supports_python_version,
    )
except ModuleNotFoundError:
    pytest.skip("Nuitka not installed", allow_module_level=True)


def test_nuitka_supports_python_version():
    """Should return true if nuitka supports the version of python."""

    # All versions of nuitka support 2.6 minimum since 1.x
    assert nuitka_supports_python_version((2, 6))
    assert not nuitka_supports_python_version((2, 5))


def test_nuitka_not_yet_supports_python_version():
    """Should return true if nuitka does not yet support the version of python."""

    assert not nuitka_not_yet_supports_python_version((2, 6))

    not_yet_supported = PythonVersions.getNotYetSupportedPythonVersions()

    if not_yet_supported:
        assert nuitka_not_yet_supports_python_version(
            version_str_to_tuple(not_yet_supported[0])
        )
