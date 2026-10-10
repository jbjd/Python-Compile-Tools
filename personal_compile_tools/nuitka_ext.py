"""Utilities for using nuitka."""

from nuitka import PythonVersions

from personal_compile_tools.converters import version_tuple_to_str


def nuitka_supports_python_version(version: tuple[int, int]) -> bool:
    """Checks if current installation of nuitka supports the provided python version.

    :param version: Python version to check
    :returns: If `version` is supported"""

    version_string: str = version_tuple_to_str(version)
    return version_string in PythonVersions.getSupportedPythonVersions()


def nuitka_raise_if_unsupported_python_version(version: tuple[int, int]) -> None:
    """Raises NotImplementedError if current installation of nuitka doesn't support
    the provided python version.

    :param version: Python version to check
    :raises NotImplementedError: If `version` is supported"""

    if not nuitka_supports_python_version(version):
        version_str: str = version_tuple_to_str(version)
        raise NotImplementedError(
            f"Python version {version_str} not supported by Nuitka"
        )
