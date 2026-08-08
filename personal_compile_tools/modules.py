"""Utilities for interacting with modules."""

from importlib import import_module


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


def module_is_one_file(module_name: str) -> str:
    """Checks if a module is a single file or a folder.

    :param module_name: Module to check
    :returns: True if module is a single file
    :raises ModuleNotFoundError: if module_name can't be imported
    """
    module = import_module(module_name)

    return not hasattr(module, "__path__")
