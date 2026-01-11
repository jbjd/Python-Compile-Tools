"""Checks to help ensure current environment is in a valid state."""

import os

if os.name == "nt":
    import ctypes


def is_root() -> bool:
    """OS Agnostic way to check if current context is root."""

    if os.name == "nt":
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

    return os.geteuid() == 0  # type: ignore[attr-defined]


def raise_if_not_root(message: str) -> None:
    """Raises if current context isn't root.

    :raises PermissionError: if not root."""
    if not is_root():
        raise PermissionError(message)
