"""Classes and functions to help analyze requirements files.
https://peps.python.org/pep-0508/"""

from enum import StrEnum
import re
from importlib.metadata import version as get_module_version

_VALID_OPERATORS: list[str] = ["<", "<=", "!=", "==", ">=", ">", "~=", "==="]


class VersionSegmentTypes(StrEnum):
    DEV = ".dev"
    ALPHA = "a"
    BETA = "b"
    CANDIDATE = "rc"
    POST = ".post"


class VersionSegment:
    """Represents a version segment as specified in pep440"""

    __slots__ = ("segment", "version")

    def __init__(self, version: int, segment: VersionSegmentTypes) -> None:
        if version < 0:
            raise ValueError(f"Version segment {segment}{version} cannot be negative")

        self.version: int = version
        self.segment: VersionSegmentTypes = segment


class VersionRule:
    """Rule that a package installer must follow e.x. >=1.0.0"""

    __slots__ = ("dev_version", "numeric_version", "operator", "post_release_version")

    def __init__(self, operator: str, version: str) -> None:
        if operator not in _VALID_OPERATORS:
            raise ValueError(f"Invalid operator {operator}")

        split_version: list[str] = version.split(".")

        for sub_version in version.split("."):
            if not sub_version.isnumeric():
                raise ValueError(f"Invalid version {version}")

        self.operator: str = operator
        self.version: str = version


class Dependency:
    """Represents a dependency of a python module"""

    __slots__ = ("name", "version_rules")

    def __init__(self, name: str, version_rules: list[VersionRule]) -> None:
        self.name: str = name
        self.version_rules: list[VersionRule] = version_rules

    def matches_installed_version(self) -> bool:
        """Returns True when this dependency's version rules match the installed
        version in current python interpreter.
        Raises PackageNotFoundError if not present"""
        installed_version: str = get_module_version(self.name)


def parse_requirements_file(
    file_path: str, encoding: str = "utf-8"
) -> list[Dependency]:
    """Given a requirements file, returns a list of
    objects representing the dependencies"""
    with open(file_path, "r", encoding=encoding) as fp:
        file_contents: str = fp.read()

    return parse_requirments(file_contents)


def parse_requirments(requirements: str) -> list[Dependency]:
    """Given contents of a requirements file, returns a list of
    objects representing the dependencies"""

    # regex slipt on \n without previous \
    for line in re.split(r"(?<=[^\\])\s*\n", requirements):
        line = re.sub(r"\s+", " ", line)

        # For now, throw out env marker
        line = line.split(";")[0]

    return []


def version_is_pep440_compliant(version: str) -> bool:
    """Verifys version against pattern found here:
    https://peps.python.org/pep-0440/"""

    version_re: str = (
        r"[0-9]+(\.[0-9]+)*((a|b|c|rc)[0-9]+)?(\.post[0-9]+)?(\.dev[0-9]+)?"
    )

    return re.match(version_re, version) is not None
