"""Classes and functions to help analyze requirements files.
https://peps.python.org/pep-0508/"""

from enum import StrEnum
import re
from importlib.metadata import version as get_module_version

_VALID_OPERATORS: list[str] = ["<", "<=", "!=", "==", ">=", ">", "~=", "==="]

_VALID_OPERATOR_RE: str = f"(?:{'|'.join(_VALID_OPERATORS)})"
_PEP440_RE: str = (
    r"[0-9]+(?:\.[0-9]+)*(?:(?:a|b|c|rc)[0-9]+)?(?:\.post[0-9]+)?(?:\.dev[0-9]+)?"
)
_PEP440_WITH_OPERATOR_RE: str = _VALID_OPERATOR_RE + _PEP440_RE
_REQUIREMENT_RE: str = (
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9\._-]*[A-Z0-9])((" + _PEP440_WITH_OPERATOR_RE + r")+)$"
)
_RULES_RE: str = f"^(?:({_PEP440_WITH_OPERATOR_RE})+)$"


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


class Requirements:
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
) -> list[Requirements]:
    """Given a requirements file, returns a list of
    objects representing the dependencies"""
    with open(file_path, "r", encoding=encoding) as fp:
        file_contents: str = fp.read()

    return parse_requirments(file_contents)


def parse_requirments(requirements: str) -> list[Requirements]:
    """Given contents of a requirements file, returns a list of
    objects representing the dependencies"""

    # regex slipt on \n without previous \
    for line in re.split(r"(?<=[^\\])\s*\n", requirements):
        line = re.sub(r"\s+", " ", line)

        # For now, throw out env marker
        line = line.split(";")[0]

    return []


def parse_requirement(requirement: str) -> Requirements:
    """Given a single line of a requirements file, returns
    data parsed into a Requirements object"""
    requirement = re.sub(r"\s+", "", requirement)

    search_result = re.search(_REQUIREMENT_RE, requirement, re.IGNORECASE)

    if search_result is None:
        raise ValueError(f"Invalid requirment {requirement}")

    name: str = search_result.group(1)
    version_rules: str = search_result.group(2)

    search_result = re.findall(_RULES_RE, version_rules)

    return search_result


def version_is_pep440_compliant(version: str) -> bool:
    """Verifys version against pattern found here:
    https://peps.python.org/pep-0440/"""

    return re.match(f"^{_PEP440_RE}$", version) is not None


test = parse_requirement("Asdg>=6.8.0<=7.0.0")
print(test)
