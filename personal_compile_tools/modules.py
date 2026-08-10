"""Utilities for interacting with modules."""

import os
import tomllib
from importlib import import_module
from typing import Any

PROJECT_FILE_NAME: str = "pyproject.toml"


def read_pyproject_file(folder: str | None = None) -> dict[str, Any]:
    """Returns contents of the pyproject file as dict.

    :param folder: Folder to check, or current working folder if None
    :returns: Dict of parsed pyproject file
    :raises OSError: If open fails
    """

    read_path: str = (
        PROJECT_FILE_NAME if folder is None else os.path.join(folder, PROJECT_FILE_NAME)
    )

    with open(read_path, "rb") as fp:
        return tomllib.load(fp)


def can_import_module(module_name: str) -> bool:
    """Returns if module was able to be imported in current context.

    :param module_name: Module to check
    :returns: True if importable, False otherwise
    """
    try:
        import_module(module_name)
    except ModuleNotFoundError:
        return False

    return True


def get_missing_modules(module_names: list[str]) -> list[str]:
    """Gets list of modules that are not able to be imported in current context.

    :param module_names: List of modules to check
    :returns: List containing subset of provided values that are missing
    """
    return [m for m in module_names if not can_import_module(m)]


def get_module_file_path(module_name: str) -> str:
    """Returns the __file__ attribute of a python module.

    :param module_name: Module to check
    :returns: Path to module
    :raises ModuleNotFoundError: if module_name can't be imported
    :raises ValueError: if __file__ is None
    """
    module = import_module(module_name)
    if module.__file__ is None:
        raise ValueError(f"Module {module_name}'s file path not set")

    return module.__file__


def module_is_one_file(module_name: str) -> bool:
    """Checks if a module is a single file or a folder.

    :param module_name: Module to check
    :returns: True if module is a single file
    :raises ModuleNotFoundError: if module_name can't be imported
    """
    module = import_module(module_name)

    return not hasattr(module, "__path__")
