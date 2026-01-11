"""Common validation checks."""

import os

if os.name == "nt":
    import ctypes


def is_root() -> bool:
    """Checks if current context isn't root.

    :Returns: True if root.
    """

    if os.name == "nt":
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

    return os.geteuid() == 0  # type: ignore[attr-defined]


def raise_if_not_root(message: str) -> None:
    """Raises if current context isn't root.

    :raises PermissionError: if not root.
    """
    if not is_root():
        raise PermissionError(message)
