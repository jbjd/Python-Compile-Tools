"""Tests for the nuitka module."""

import pytest

from personal_compile_tools.converters import version_str_to_tuple

try:
    from nuitka import PythonVersions

    from personal_compile_tools.nuitka_ext import (
        nuitka_raise_if_unsupported_python_version,
        nuitka_supports_python_version,
    )
except ModuleNotFoundError:
    pytest.skip("Nuitka not installed", allow_module_level=True)

_supported_version_example: tuple[int, int] = version_str_to_tuple(  # type: ignore[assignment]
    PythonVersions.getSupportedPythonVersions()[0]
)
_unsupported_version_example: tuple[int, int] = (1, 99)


def test_nuitka_supports_python_version():
    """Should return true if nuitka supports the version of python."""

    assert nuitka_supports_python_version(_supported_version_example)
    assert not nuitka_supports_python_version(_unsupported_version_example)


def test_nuitka_raise_if_unsupported_python_version():
    """Should raise if nuitka does not yet support the version of python."""

    nuitka_raise_if_unsupported_python_version(_supported_version_example)

    with pytest.raises(NotImplementedError, match="not supported by Nuitka"):
        nuitka_raise_if_unsupported_python_version(_unsupported_version_example)
