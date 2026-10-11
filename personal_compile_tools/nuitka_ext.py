"""Utilities for using nuitka."""

import sys

from nuitka import PythonVersions

from personal_compile_tools.converters import version_tuple_to_str


def nuitka_supports_python_version(version: tuple[int, int]) -> bool:
    """Checks if current installation of nuitka supports the provided python version.

    :param version: Python version to check
    :returns: If `version` is supported"""

    version_string: str = version_tuple_to_str(version)
    return version_string in PythonVersions.getSupportedPythonVersions()


def nuitka_raise_if_unsupported_python_version(
    version: tuple[int, int] | None = None,
) -> None:
    """Raises NotImplementedError if current installation of nuitka doesn't support
    the provided python version.

    :param version: Python version to check, or current interpreter if None
    :raises NotImplementedError: If `version` is supported"""

    if version is None:
        version = sys.version_info[:2]

    if not nuitka_supports_python_version(version):
        raise NotImplementedError(f"Python version {version} not supported by Nuitka")
