"""Checks to help ensure current env is in a valid state"""

import os

if os.name == "nt":
    import ctypes


def is_root() -> bool:
    """OS Agnostic way to check if current context is root"""

    if os.name == "nt":
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore

    return os.geteuid() == 0  # type: ignore
