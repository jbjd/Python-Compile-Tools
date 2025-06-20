"""Classes and functions to help analyze requirements files.
https://peps.python.org/pep-0508/"""

import re
from enum import IntEnum
from importlib.metadata import version as get_module_version

from personal_compile_tools.converters import version_str_to_tuple

_VALID_OPERATORS: list[str] = ["<", "<=", "!=", "==", ">=", ">", "~=", "==="]

_VALID_OPERATOR_RE: str = "|".join(_VALID_OPERATORS)

_PEP440_RE: str = (
    r"^([0-9]+(?:\.[0-9]+)*)((?:a|b|rc)[0-9]+)?(\.post[0-9]+)?(\.dev[0-9]+)?$"
)

_OPERATOR_WITH_VERSION_RE: str = f"({_VALID_OPERATOR_RE})" + r"([a-zA-Z0-9\.\-_]+)"
_REQUIREMENT_RE: str = (
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9\._-]*[A-Z0-9])((?:" + _VALID_OPERATOR_RE + r").+)$"
)

_NO_SEGMENT_VALUE: int = -1


class PreSegmentType(IntEnum):
    """Represents pre-release versions in pep440"""

    ALPHA = 0
    BETA = 1
    CANDIDATE = 2
    NONE = 3


class Version:
    """Represents a version as specified in pep440
    https://peps.python.org/pep-0440/"""

    __slots__ = (
        "is_literal",
        "raw_version",
        "release_version",
        "pre_segment_type",
        "pre_segment",
        "post_segment",
        "dev_segment",
    )

    def __init__(self, raw_version: str, is_literal: bool = False) -> None:
        self.is_literal: bool = is_literal
        self.raw_version: str
        self.release_version: tuple[int, ...]
        self.pre_segment_type: PreSegmentType
        self.pre_segment: int
        self.post_segment: int
        self.dev_segment: int

        if is_literal:
            self.raw_version = raw_version
            self.release_version = tuple()
            self.pre_segment_type = PreSegmentType.NONE
            self.pre_segment = _NO_SEGMENT_VALUE
            self.post_segment = _NO_SEGMENT_VALUE
            self.dev_segment = _NO_SEGMENT_VALUE
            return

        self.raw_version = normalize_version(raw_version)

        # TODO: Refactor to break this up more

        version_search = re.search(_PEP440_RE, self.raw_version)

        if version_search is None:
            raise ValueError(f"Invalid version {raw_version}")

        # release_version can't be None here, others can since
        # they are marked optional by a "?" in the regex
        release_version: str
        pre_segment: str | None
        post_segment: str | None
        dev_segment: str | None
        release_version, pre_segment, post_segment, dev_segment = (
            version_search.groups()
        )

        self.release_version = version_str_to_tuple(release_version)

        # 1.0.0 is same as 1 so remove training 0s
        while len(self.release_version) > 1 and self.release_version[-1] == 0:
            self.release_version = self.release_version[:-1]

        self.pre_segment_type = self._get_pre_segment_type(pre_segment)
        self.pre_segment = self._get_segment_value(pre_segment, "abrc")
        self.post_segment = self._get_segment_value(post_segment, ".post")
        self.dev_segment = self._get_segment_value(dev_segment, ".dev")

    def __str__(self) -> str:
        return self.raw_version

    def __eq__(self, other) -> bool:
        if self.is_literal and other.is_literal:
            return self.raw_version == other.raw_version

        return (
            self.is_literal == other.is_literal
            and self.release_version == other.release_version
            and self.pre_segment == other.pre_segment
            and self.pre_segment_type == other.pre_segment_type
            and self.post_segment == other.post_segment
            and self.dev_segment == other.dev_segment
        )

    def __gt__(self, other) -> bool:
        if self.is_literal or other.is_literal:
            raise ValueError("Literal versions can't be greater or less then")

        if self.release_version != other.release_version:
            return self.release_version > other.release_version

        if self.pre_segment_type != other.pre_segment_type:
            return self.pre_segment_type > other.pre_segment_type

        if self.pre_segment != other.pre_segment:
            return self.pre_segment > other.pre_segment

        if self.post_segment != other.post_segment:
            return self.post_segment > other.post_segment

        # Weird edge case: presence of dev segment implies and earlier version
        # So consider version greater only if its present. If either version
        # was missing the dev segment, we need to consider it "greater"
        # for having a lesser value
        if self.dev_segment >= 0 and other.dev_segment >= 0:
            return self.dev_segment > other.dev_segment
        else:
            return self.dev_segment < other.dev_segment

    def __ge__(self, other) -> bool:
        return self > other or self == other

    @staticmethod
    def _get_pre_segment_type(parsed_segment: str | None) -> PreSegmentType:
        if parsed_segment is None:
            return PreSegmentType.NONE
        elif parsed_segment.startswith("a"):
            return PreSegmentType.ALPHA
        elif parsed_segment.startswith("b"):
            return PreSegmentType.BETA
        else:
            return PreSegmentType.CANDIDATE

    @staticmethod
    def _get_segment_value(parsed_segment: str | None, to_strip: str) -> int:
        return (
            int(parsed_segment.lstrip(to_strip))
            if parsed_segment is not None
            else _NO_SEGMENT_VALUE
        )

    def compare_up_to(self, other: "Version", count: int) -> bool:
        """Given version like 1.2.3 and 1.2.4, only compare up to count number of parts.

        If count is 2, then check "1.2" == "1.2" """
        return self.release_version[:count] == other.release_version[:count]


class VersionRule:
    """Rule that a package installer must follow e.x. >=1.0.0"""

    __slots__ = ("_fuzzy_match", "_operator", "_version")

    def __init__(self, operator: str, version: str) -> None:
        if operator not in _VALID_OPERATORS:
            raise ValueError(f"Invalid operator {operator}")

        if version.endswith(".*"):
            version = version[:-2]
            self._fuzzy_match = True
        else:
            self._fuzzy_match = False

        if self._fuzzy_match and operator not in ("==", "!="):
            raise ValueError(".* can only be used with '==' or '!=' operators")

        self._operator: str = operator

        is_literal: bool = operator == "==="
        self._version = Version(version, is_literal)

        if self._operator == "~=" and len(self._version.release_version) < 2:
            raise ValueError(
                "Use of '~=' operator requires release version to have "
                f"more than one segment, {self._version.release_version} has only one"
            )

    def __str__(self) -> str:
        rule: str = f"{self._operator}{self._version}"

        if self._fuzzy_match:
            rule += ".*"

        return rule

    def __eq__(self, other) -> bool:
        return (
            self._operator == other._operator
            and self._version == other._version
            and self._fuzzy_match == other._fuzzy_match
        )

    def version_is_compliant(self, installed_version: str) -> bool:
        """Returns True if provided version
        is compliant with the rule this object represents"""

        use_literal_compare: bool = self._operator == "==="
        installed_version_parsed = Version(installed_version, use_literal_compare)

        match self._operator:
            case "~=":
                # ~=1.4.5 is same as >=1.4.5,== 1.4.*
                compare_up_to: int = len(self._version.release_version) - 1

                return self._version.compare_up_to(
                    installed_version_parsed, compare_up_to
                ) and (installed_version_parsed >= self._version)
            case ">":
                return installed_version_parsed > self._version
            case ">=":
                return installed_version_parsed >= self._version
            case "<":
                return installed_version_parsed < self._version
            case "<=":
                return installed_version_parsed <= self._version
            case "===":
                return installed_version_parsed == self._version
            case "!=":
                return not self._compare_versions_with_fuzzy_match(
                    installed_version_parsed
                )
            case _:
                return self._compare_versions_with_fuzzy_match(installed_version_parsed)

    def _compare_versions_with_fuzzy_match(self, other: Version) -> bool:

        # If fuzzy is true, only release version will be set
        if self._fuzzy_match:
            compare_up_to: int = len(self._version.release_version)

            return self._version.compare_up_to(other, compare_up_to)

        return self._version == other


class Requirement:
    """Represents a dependency of a python module"""

    __slots__ = ("name", "rules")

    def __init__(self, name: str, version_rules: list[VersionRule]) -> None:
        self.name: str = name
        self.rules: list[VersionRule] = version_rules

    def __str__(self) -> str:
        return self.name + "".join(map(str, self.rules))

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name
            and len(self.rules) == len(other.rules)
            and all(rule1 == rule2 for rule1, rule2 in zip(self.rules, other.rules))
        )

    def matches_installed_version(self) -> bool:
        """Returns True when this dependency's version rules match the installed
        version in current python interpreter.
        Raises importlib.metadata.PackageNotFoundError if not present"""
        installed_version: str = get_module_version(self.name)

        return all(rule.version_is_compliant(installed_version) for rule in self.rules)


def parse_requirements_file(
    file_path: str, encoding: str = "utf-8"
) -> list[Requirement]:
    """Given a requirements file, returns a list of
    objects representing the dependencies"""
    with open(file_path, "r", encoding=encoding) as fp:
        file_contents: str = fp.read()

    return parse_requirements(file_contents)


def parse_requirements(raw_requirements: str) -> list[Requirement]:
    """Given contents of a requirements file, returns a list of
    objects representing the dependencies"""

    requirements: list[Requirement] = []

    # regex slipt on \n without previous \
    raw_requirements = raw_requirements.strip()
    for line in re.split(r"(?<=[^\\])\s*\n", raw_requirements):
        # For now, throw out env marker
        line = line.split(";")[0]

        requirement: Requirement = parse_requirement(line)
        requirements.append(requirement)

    return requirements


def parse_requirement(requirement: str) -> Requirement:
    """Given a single line of a requirements file, returns
    data parsed into a Requirements object"""
    requirement = re.sub(r"(\s+|\\\s*\n)", "", requirement)

    search_result = re.search(_REQUIREMENT_RE, requirement, re.IGNORECASE)

    if search_result is None:
        raise ValueError(f"Invalid requirement {requirement}")

    name: str = search_result.group(1)
    version_rules_unparsed: str = search_result.group(2)

    split_version_rules_unparsed: list[tuple[str, str]] = re.findall(
        _OPERATOR_WITH_VERSION_RE, version_rules_unparsed
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

    # Normalize zeros
    version = re.sub(r"\.00+", ".0", version)

    # Don't turn rc -> rrc, only c -> rc
    if "rc" not in version:
        version = version.replace("c", "rc", 1)

    return version.replace("alpha", "a", 1).replace("beta", "b", 1)


def version_is_pep440_compliant(version: str) -> bool:
    """Verifys version against pattern found here:
    https://peps.python.org/pep-0440/"""

    return re.match(f"^{_PEP440_RE}$", normalize_version(version)) is not None
