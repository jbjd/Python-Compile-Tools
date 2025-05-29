import os

if os.name == "nt":
    import ctypes


def is_root() -> bool:
    """OS Agnostic way to check if current context is root"""
    is_root: bool
    if os.name == "nt":
        is_root = ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore
    else:
        is_root = os.geteuid() == 0  # type: ignore

    return is_root
