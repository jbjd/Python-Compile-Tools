from importlib import import_module


def get_module_file_path(module_name: str):
    """Returns the install folder of a python module.
    Raises ValueError if the module's __file__ attribute is None."""
    module = import_module(module_name)
    if module.__file__ is None:
        raise ValueError(f"Module {module_name}'s file path not set")

    return module.__file__
