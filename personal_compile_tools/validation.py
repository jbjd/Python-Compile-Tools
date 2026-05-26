"""Common validation checks."""

import sys

if sys.platform == "win32":  # pragma: no cover
    import ctypes
else:  # pragma: no cover
    import os


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
