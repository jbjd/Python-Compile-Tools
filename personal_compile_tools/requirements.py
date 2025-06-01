"""Classes and functions to help analyze requirements files.
https://peps.python.org/pep-0508/"""

import re
from typing import NoReturn

_VALID_OPERATORS: list[str] = ["<", "<=", "!=", "==", ">=", ">", "~=", "==="]

_VALID_OPERATOR_RE: str = "|".join(_VALID_OPERATORS)

_PEP440_RE_NO_CAP: str = (
    r"[0-9]+(?:\.[0-9]+)*(?:(?:a|b|rc)[0-9]+)?(?:\.post[0-9]+)?(?:\.dev[0-9]+)?"
)
_PEP440_RE: str = (
    r"([0-9]+(?:\.[0-9]+)*)((?:a|b|rc)[0-9]+)?(\.post[0-9]+)?(\.dev[0-9]+)?"
)

_PEP440_WITH_OPERATOR_RE: str = f"({_VALID_OPERATOR_RE})({_PEP440_RE_NO_CAP})"
_REQUIREMENT_RE: str = (
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9\._-]*[A-Z0-9])(("
    + f"(?:{_VALID_OPERATOR_RE})"
    + _PEP440_RE_NO_CAP
    + r")+)$"
)


class Version:
    """Represents a version as specified in pep440
    https://peps.python.org/pep-0440/"""

    __slots__ = (
        "dev_segment",
        "operator",
        "post_segment",
        "pre_segment",
        "raw_version",
        "release_version",
    )

    def __init__(self, version: str) -> None:
        version = normalize_version(version)
        test = re.search(_PEP440_RE, version)

        if test is None:
            self._raise_invalid_version(version)

        # TODO: Handle segments
        release_version, pre_segment, post_segment, dev_segment = test.groups()

        if release_version is None:
            self._raise_invalid_version(version)

        self.release_version: str = release_version
        self.raw_version: str = version
        self.pre_segment: str | None = None
        self.post_segment: str | None = None
        self.dev_segment: str | None = None

    def __eq__(self, other: "Version") -> bool:
        return self.raw_version == other.raw_version

    @staticmethod
    def _raise_invalid_version(version: str) -> NoReturn:
        raise ValueError(f"Invalid version {version}")


class VersionRule:
    """Rule that a package installer must follow e.x. >=1.0.0"""

    __slots__ = ("operator", "version")

    def __init__(self, operator: str, version: str) -> None:
        if operator not in _VALID_OPERATORS:
            raise ValueError(f"Invalid operator {operator}")

        self.version = Version(version)

    def version_is_compliant(self, test_version_raw: str) -> bool:
        """Returns True if provided version
        is compliant with the rule this object represents"""
        test_version = Version(test_version_raw)

        # TODO: Handle all
        match self.operator:
            case "!=":
                return test_version != self.version.raw_version
            case _:
                return test_version == self.version.raw_version


class Requirement:
    """Represents a dependency of a python module"""

    __slots__ = ("name", "version_rules")

    def __init__(self, name: str, version_rules: list[VersionRule]) -> None:
        self.name: str = name
        self.version_rules: list[VersionRule] = version_rules

    def matches_installed_version(self) -> bool:
        """Returns True when this dependency's version rules match the installed
        version in current python interpreter.
        Raises PackageNotFoundError if not present"""
        return all(
            version_rule.installed_version_is_compliant(self.name)
            for version_rule in self.version_rules
        )


def parse_requirements_file(
    file_path: str, encoding: str = "utf-8"
) -> list[Requirement]:
    """Given a requirements file, returns a list of
    objects representing the dependencies"""
    with open(file_path, "r", encoding=encoding) as fp:
        file_contents: str = fp.read()

    return parse_requirments(file_contents)


def parse_requirments(raw_requirements: str) -> list[Requirement]:
    """Given contents of a requirements file, returns a list of
    objects representing the dependencies"""

    requirements: list[Requirement] = []

    # regex slipt on \n without previous \
    raw_requirements = raw_requirements.strip()
    for line in re.split(r"(?<=[^\\])\s*\n", raw_requirements):
        line = re.sub(r"\s+", " ", line)

        # For now, throw out env marker
        line = line.split(";")[0]

        requirement: Requirement = parse_requirement(line)
        requirements.append(requirement)

    return requirements


def parse_requirement(requirement: str) -> Requirement:
    """Given a single line of a requirements file, returns
    data parsed into a Requirements object"""
    requirement = re.sub(r"\s+", "", requirement)

    search_result = re.search(_REQUIREMENT_RE, requirement, re.IGNORECASE)

    if search_result is None:
        raise ValueError(f"Invalid requirment {requirement}")

    name: str = search_result.group(1)
    version_rules_unparsed: str = search_result.group(2)

    split_version_rules_unparsed: list[tuple[str, str]] = re.findall(
        _PEP440_WITH_OPERATOR_RE, version_rules_unparsed
    )

    version_rules: list[VersionRule] = [
        VersionRule(operator, version)
        for operator, version in split_version_rules_unparsed
    ]

    return Requirement(name, version_rules)


def normalize_version(version: str) -> str:
    """Normalizes version with rules found here:
    https://peps.python.org/pep-0440/"""
    # TODO: this is not complete
    return version.replace("alpha", "a", 1).replace("beta", "b", 1)


def version_is_pep440_compliant(version: str) -> bool:
    """Verifys version against pattern found here:
    https://peps.python.org/pep-0440/"""

    return re.match(f"^{_PEP440_RE_NO_CAP}$", normalize_version(version)) is not None
