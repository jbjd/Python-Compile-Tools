"""Common validation checks."""

import sys

from personal_compile_tools.converters import version_tuple_to_str
from personal_compile_tools.requirements import make_version_rules

if sys.platform == "win32":  # pragma: no cover
    import ctypes
else:  # pragma: no cover
    import os

from personal_compile_tools.modules import read_pyproject_file


def is_root() -> bool:
    """Checks if current context isn't root.

    :Returns: True if root.
    """

    if sys.platform == "win32":
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        return os.geteuid() == 0


def raise_if_not_root(message: str) -> None:
    """Raises if current context isn't root.

    :raises PermissionError: if not root.
    """
    if not is_root():
        raise PermissionError(message)


def raise_if_unsupported_python_version_pyproject(
    python_version: tuple[int, int] | tuple[int, int, int] | None = None,
    project_folder: str | None = None,
) -> None:
    """Raises NotImplementedError if current python interpreter isn't a supported
    version in the pyproject.toml file.

    :param python_version: Version to compare against, or current interpreter if None
    :param project_folder: Folder to check, or current working folder if None
    :raises NotImplementedError: If unsupported version
    :raises KeyError: If project file is missing [project] or key 'requires-python'
    :raises OSError: If open fails
    """

    requires: str = read_pyproject_file(project_folder)["project"]["requires-python"]

    rules = make_version_rules(requires)

    used_python: str = version_tuple_to_str(
        sys.version_info[:3] if python_version is None else python_version
    )

    if any(not rule.version_is_compliant(used_python) for rule in rules):
        raise NotImplementedError(
            f"Python version {used_python} not supported by this project. "
            f"Supports {requires}"
        )
