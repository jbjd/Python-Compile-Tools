"""Utilities for interacting with modules."""

from importlib import import_module


def get_module_file_path(module_name: str) -> str:
    """Returns the __file__ attribute of a python module.

    :param module_name: Module to check.
    :returns: Path to module.
    :raises ValueError: if __file__ is None.
    """
    module = import_module(module_name)
    if module.__file__ is None:
        raise ValueError(f"Module {module_name}'s file path not set")

    return module.__file__
