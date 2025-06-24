"""Classes and functions to help analyze requirements files.
https://peps.python.org/pep-0508/"""

import re
from abc import ABC, abstractmethod
from enum import IntEnum
from importlib.metadata import version as get_module_version
from typing import Self

from personal_compile_tools.converters import version_str_to_tuple, version_tuple_to_str

_VALID_OPERATORS: list[str] = ["<", "<=", "!=", "==", ">=", ">", "~=", "==="]

_VALID_OPERATOR_RE: str = "|".join(_VALID_OPERATORS)

_PEP440_RE: str = (
    r"^([0-9]+(?:\.[0-9]+)*)(?:(?:\.|-|_)?((?:alpha|a|beta|b|rc|c)[0-9]+))?((?:\.|-|_)?post[0-9]+)?((?:\.|-|_)?dev[0-9]+)?$"  # noqa: E501
)

_OPERATOR_WITH_VERSION_RE: str = f"({_VALID_OPERATOR_RE})" + r"([a-z0-9\.\-_]+)"
_REQUIREMENT_RE: str = (
    r"^([a-z0-9](?:[a-z0-9\._-]*[a-z0-9])?)((?:" + _VALID_OPERATOR_RE + r").+)$"
)

NO_SEGMENT_VALUE: int = -1


class PreSegmentType(IntEnum):
    """Represents pre-release versions in pep440"""

    ALPHA = 0
    BETA = 1
    CANDIDATE = 2
    NONE = 3


class Version(ABC):

    __slots__ = ("raw_version",)

    def __init__(self, raw_version: str):
        self.raw_version: str = raw_version

    def __str__(self) -> str:
        return self.raw_version

    @abstractmethod
    def __eq__(self, other) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def __gt__(self, other) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def __ge__(self, other) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def get_version_parts_len(self) -> int:  # pragma: no cover
        """Returns number of parts in the version.
        e.x. 1.2.3 returns 3"""
        pass

    @abstractmethod
    def compare_parts_up_to(self, other: Self, count: int) -> bool:  # pragma: no cover
        """Given version like 1.2.3 and 1.2.4, only compare up to count number of parts.

        If count is 2, then check "1.2" == "1.2" """
        pass


class VersionLiteral(Version):
    """Represents a literal version, where equality
    is strictly checked"""

    __slots__ = ()

    GT_LT_ERROR_MESSAGE: str = "Literal versions can't compare greater or less then"

    def __eq__(self, other) -> bool:
        return self.raw_version == other.raw_version

    def __gt__(self, other) -> bool:
        raise ValueError(self.GT_LT_ERROR_MESSAGE)

    def __ge__(self, other) -> bool:
        raise ValueError(self.GT_LT_ERROR_MESSAGE)

    def get_version_parts_len(self) -> int:
        return 1

    def compare_parts_up_to(self, other: Self, count: int) -> bool:
        raise ValueError("Literal versions can't compare up to")


class VersionPep440(Version):
    """Represents a version as specified in pep440
    https://peps.python.org/pep-0440/"""

    __slots__ = (
        "release_version",
        "pre_segment_type",
        "pre_segment",
        "post_segment",
        "dev_segment",
    )

    def __init__(
        self,
        raw_version: str,
        keep_trailing_zeros: bool = False,
    ) -> None:
        self.release_version: tuple[int, ...]
        self.pre_segment_type: PreSegmentType
        self.pre_segment: int
        self.post_segment: int
        self.dev_segment: int

        (
            self.release_version,
            self.pre_segment_type,
            self.pre_segment,
            self.post_segment,
            self.dev_segment,
        ) = parse_pep440_version(raw_version, keep_trailing_zeros)

        raw_version = construct_pep440_version(
            self.release_version,
            self.pre_segment_type,
            self.pre_segment,
            self.post_segment,
            self.dev_segment,
        )
        super().__init__(raw_version)

    def __eq__(self, other) -> bool:
        return (
            self.release_version == other.release_version
            and self.pre_segment == other.pre_segment
            and self.pre_segment_type == other.pre_segment_type
            and self.post_segment == other.post_segment
            and self.dev_segment == other.dev_segment
        )

    def __gt__(self, other) -> bool:
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

    def get_version_parts_len(self) -> int:
        return len(self.release_version)

    def compare_parts_up_to(self, other: Self, count: int) -> bool:
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

        is_literal: bool = self._use_literal_compare()
        self._version: Version = make_version(version, is_literal, self._fuzzy_match)

        if self._operator == "~=" and self._version.get_version_parts_len() < 2:
            raise ValueError(
                "Use of '~=' operator requires release version to have "
                f"more than one segment, {self._version} has only one"
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

        is_literal: bool = self._use_literal_compare()
        installed_version_parsed = make_version(
            installed_version, is_literal, self._fuzzy_match
        )

        match self._operator:
            case "~=":
                # ~=1.4.5 is same as >=1.4.5,== 1.4.*
                compare_up_to: int = self._version.get_version_parts_len() - 1

                return self._version.compare_parts_up_to(
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
        """Checks if self == other or if fuzzy match is True, checks
        up to the number of parts in self's version.

        So if self is 1.2 and other is 1.2.3, fuzzy match says "1.2" == "1.2" """

        # If fuzzy is true, only release version can be set
        if self._fuzzy_match:
            compare_up_to: int = self._version.get_version_parts_len()

            return self._version.compare_parts_up_to(other, compare_up_to)

        return self._version == other

    def _use_literal_compare(self) -> bool:
        """Returns True if compare should be strictly literal"""
        return self._operator == "==="


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


def make_version(
    raw_version: str, is_literal: bool, keep_trailing_zeros: bool = False
) -> Version:
    """Returns correct version class based on is_literal.
    keep_trailing_zeros is only passed if is_literal is False"""
    return (
        VersionLiteral(raw_version)
        if is_literal
        else VersionPep440(raw_version, keep_trailing_zeros)
    )


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
        _OPERATOR_WITH_VERSION_RE, version_rules_unparsed, flags=re.IGNORECASE
    )

    version_rules: list[VersionRule] = [
        VersionRule(operator, version)
        for operator, version in split_version_rules_unparsed
    ]

    return Requirement(name, version_rules)


def normalize_version(version: str) -> str:
    """Normalizes version with rules found here:
    https://peps.python.org/pep-0440/"""

    return construct_pep440_version(*parse_pep440_version(version))


def version_is_pep440_compliant(version: str) -> bool:
    """Verifies version against pattern found here:
    https://peps.python.org/pep-0440/"""

    return re.match(f"^{_PEP440_RE}$", version, flags=re.IGNORECASE) is not None


def construct_pep440_version(
    release_version: tuple[int, ...],
    pre_segment_type: PreSegmentType = PreSegmentType.NONE,
    pre_segment: int = NO_SEGMENT_VALUE,
    post_segment: int = NO_SEGMENT_VALUE,
    dev_segment: int = NO_SEGMENT_VALUE,
) -> str:
    """Given parts of a pep440 version, return a str
    of the version in the normalized form recommended
    by pep440

    A Segment will be considered absent if its negative"""
    version: str = version_tuple_to_str(release_version)

    if pre_segment < 0 and pre_segment_type != PreSegmentType.NONE:
        raise ValueError("Must specify a value for pre-release segment if its present")

    if pre_segment >= 0 and pre_segment_type == PreSegmentType.NONE:
        raise ValueError("Can't have pre-release version number if its not present")

    if pre_segment >= 0:
        if pre_segment_type == PreSegmentType.ALPHA:
            version += "a"
        elif pre_segment_type == PreSegmentType.BETA:
            version += "b"
        elif pre_segment_type == PreSegmentType.CANDIDATE:
            version += "rc"

        version += str(pre_segment)

    if post_segment >= 0:
        version += f".post{post_segment}"

    if dev_segment >= 0:
        version += f".dev{dev_segment}"

    return version


def parse_pep440_version(
    raw_version: str, keep_trailing_zeros: bool = False
) -> tuple[tuple[int, ...], PreSegmentType, int, int, int]:
    """Given a pep440 compliant version, turn it into its
    parts. A release version, pre release segment type,
    pre release segment, post release segment, and
    dev release segment.

    Segments that are missing are given a value of -1"""
    version_search = re.search(_PEP440_RE, raw_version, flags=re.IGNORECASE)

    if version_search is None:
        raise ValueError(f"Invalid version {raw_version}")

    release_version_raw: str
    pre_segment_raw: str | None
    post_segment_raw: str | None
    dev_segment_raw: str | None
    release_version_raw, pre_segment_raw, post_segment_raw, dev_segment_raw = (
        version_search.groups()
    )

    release_version = version_str_to_tuple(release_version_raw)

    # 1.0.0 is same as 1 so remove training 0s
    # Optional to keep them for cases like ~= operator
    if not keep_trailing_zeros:
        while len(release_version) > 1 and release_version[-1] == 0:
            release_version = release_version[:-1]

    pre_segment_type = _get_pre_segment_type(pre_segment_raw)
    pre_segment = _get_segment_value(pre_segment_raw)
    post_segment = _get_segment_value(post_segment_raw)
    dev_segment = _get_segment_value(dev_segment_raw)

    return (release_version, pre_segment_type, pre_segment, post_segment, dev_segment)


def _get_pre_segment_type(parsed_segment: str | None) -> PreSegmentType:
    """Returns the type of pre-release based on the parsed segment"""
    if parsed_segment is None:
        return PreSegmentType.NONE
    elif parsed_segment.startswith("a"):
        return PreSegmentType.ALPHA
    elif parsed_segment.startswith("b"):
        return PreSegmentType.BETA
    else:
        return PreSegmentType.CANDIDATE


def _get_segment_value(parsed_segment: str | None) -> int:
    """Returns the int value of the parsed segment or -1 if
    the segment is None"""
    return (
        int(re.sub("[^0-9]", "", parsed_segment))
        if parsed_segment is not None
        else NO_SEGMENT_VALUE
    )
