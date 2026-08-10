"""Utilities for using nuitka."""

from nuitka import PythonVersions

from personal_compile_tools.converters import version_tuple_to_str


def nuitka_supports_python_version(version: tuple[int, int]) -> bool:
    """Checks if current installation of nuitka supports the provided python version.

    :param version: Python version to check
    :returns: If `version` is supported"""

    version_string: str = version_tuple_to_str(version)
    return version_string in PythonVersions.getSupportedPythonVersions()


def nuitka_not_yet_supports_python_version(version: tuple[int, int]) -> bool:
    """Checks if current installation of nuitka does not yet support the provided
    python version.

    :param version: Python version to check
    :returns: If `version` is not yet supported"""

    version_string: str = version_tuple_to_str(version)
    return version_string in PythonVersions.getNotYetSupportedPythonVersions()
