from importlib.metadata import version as get_module_version


class Dependency:
    """Represents a dependency of a python module"""

    __slots__ = ("name", "version")

    def __init__(self, name: str, version: str) -> None:
        self.name: str = name
        self.version: str = version

    def matches_installed_version(self) -> bool:
        """Returns True when this dependency's version matches the installed
        version in current python interpreter. raises PackageNotFoundError
        if not present"""
        return get_module_version(self.name) == self.version
