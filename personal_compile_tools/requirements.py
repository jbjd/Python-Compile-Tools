"""Classes and functions to help analyze requirements files.

https://peps.python.org/pep-0508/
"""

import platform
import re
from collections.abc import Callable
from enum import StrEnum
from importlib.metadata import version as get_module_version

from packaging.version import InvalidVersion, Version
from packaging.version import parse as _version_parse


class Operators(StrEnum):
    """Valid comparison operators that can be used in a requirements file."""

    EQUALS = "=="
    NOT_EQUALS = "!="
    GT = ">"
    GT_OR_EQUALS = ">="
    LT = "<"
    LT_OR_EQUALS = "<="
    COMPATIBLE = "~="
    ARBITRARY_EQUALITY = "==="
    DIRECT_REFERENCE = "@"


class EnvMarkerOperators(StrEnum):
    """Valid comparison operators that can be used for env markers
    in a requirements file.
    """

    EQUALS = "=="
    NOT_EQUALS = "!="
    IN = " in "
    NOT_IN = " not in "


class EnvMarkerExprs(StrEnum):
    """Valid expressions that can be used for env markers
    in a requirements file.
    """

    PLATFORM_SYS = "platform_system"


_VALID_OPERATORS: list[str] = [op for op in Operators]
_VALID_ENV_MARKER_OPERATORS: list[str] = [op for op in EnvMarkerOperators]


_VALID_OPERATOR_RE: str = "|".join(_VALID_OPERATORS)
_VALID_ENV_MARKER_OPERATORS_RE = "|".join(_VALID_ENV_MARKER_OPERATORS)

_OPERATOR_WITH_VERSION_RE: str = f"({_VALID_OPERATOR_RE})" + r"([a-z0-9\.\-_*]+)"
_REQUIREMENT_RE: str = (
    r"^([a-z0-9](?:[a-z0-9\._-]*[a-z0-9])?)((?:" + _VALID_OPERATOR_RE + r").+)$"
)

_ENV_MARKER_RE: str = r"^\s*(.+?)(" + _VALID_ENV_MARKER_OPERATORS_RE + r")(.+?)\s*$"


class VersionRule:
    """Rule that a package installer must follow that also complies
    with packaging.version.parse rules."""

    __slots__ = ("_fuzzy_match", "_operator", "_raw_version", "_version")

    FUZZY_MATCH_ENDING: str = ".*"

    def __init__(self, operator: Operators, version: str) -> None:
        self._fuzzy_match = version.endswith(self.FUZZY_MATCH_ENDING)
        if self._fuzzy_match:
            version = version[:-2]
            if not self._version_is_all_numeric(version):
                raise InvalidVersion(".* can't be used with segments")

        if self._fuzzy_match and operator not in (
            Operators.EQUALS,
            Operators.NOT_EQUALS,
        ):
            raise ValueError(".* can only be used with '==' or '!=' operators")

        self._operator: Operators = operator
        self._raw_version: str = version
        self._version: Version

        if is_literal_operator(operator):
            self._version = Version("0")  # Placeholder
        else:
            self._version = _version_parse(version)

            if operator == "~=" and len(self._version.release) < 2:
                raise ValueError(
                    "Use of '~=' operator requires release version to have "
                    f"more than one segment, {self._version} has only one"
                )

    def __str__(self) -> str:
        if is_literal_operator(self._operator):
            return f"{self._operator}{self._raw_version}"

        rule: str = f"{self._operator}{self._version}"

        if self._fuzzy_match:
            rule += self.FUZZY_MATCH_ENDING

        return rule

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, VersionRule)
            and self._operator == other._operator
            and self._fuzzy_match == other._fuzzy_match
            and (
                self._raw_version == other._raw_version
                if is_literal_operator(self._operator)
                else self._version == other._version
            )
        )

    def __hash__(self) -> int:
        if is_literal_operator(self._operator):
            return hash(self._raw_version + self._operator)

        return hash(str(self._version) + self._operator + str(self._fuzzy_match))

    @property
    def operator(self) -> str:
        return self._operator

    @property
    def version(self) -> str:
        return (
            self._raw_version
            if is_literal_operator(self._operator)
            else str(self._version)
        )

    def version_is_compliant(
        self,
        version: str,
        direct_reference_handler: Callable[[str, str], bool] | None = None,
    ) -> bool:
        """Checks if `version` is compliant with this rule.

        :param version: To check against
        :direct_reference_handler: Callable taking first the input `version` and second
            the reference version that determines how direct references `@` are handled
        :raises ValueError: If `direct_reference_handler` is None and a
            direct refernce is encountered."""
        result: bool
        match self._operator:
            case Operators.COMPATIBLE:
                # ~=1.4.5 is same as >=1.4.5 and ==1.4.*
                compare_up_to: int = len(self._version.release) - 1
                parsed_other_version: Version = _version_parse(version)

                result = (
                    self._compare_version_up_to_self(
                        parsed_other_version, compare_up_to
                    )
                    and parsed_other_version >= self._version
                )
            case Operators.GT:
                result = _version_parse(version) > self._version
            case Operators.GT_OR_EQUALS:
                result = _version_parse(version) >= self._version
            case Operators.LT:
                result = _version_parse(version) < self._version
            case Operators.LT_OR_EQUALS:
                result = _version_parse(version) <= self._version
            case Operators.NOT_EQUALS:
                result = not self._compare_versions_with_fuzzy_match(version)
            case Operators.ARBITRARY_EQUALITY:
                result = version == self._raw_version
            case Operators.DIRECT_REFERENCE:
                if direct_reference_handler is None:
                    raise ValueError(
                        "Can't determine if direct references are compliant and no "
                        "handler was passed."
                    )
                result = direct_reference_handler(version, self._raw_version)
            case _:
                result = self._compare_versions_with_fuzzy_match(version)

        return result

    def _compare_versions_with_fuzzy_match(self, other_version: str) -> bool:
        """Checks if self == other or if fuzzy match is True, checks
        up to the number of parts in self's version.

        So if self is 1.2 and other is 1.2.3, fuzzy match says "1.2" == "1.2".
        """

        parsed_other_version: Version = _version_parse(other_version)

        # If fuzzy is true, only release version can be set
        if self._fuzzy_match:
            compare_up_to: int = len(self._version.release)

            return self._compare_version_up_to_self(parsed_other_version, compare_up_to)

        return parsed_other_version == self._version

    def _compare_version_up_to_self(
        self, other_version: Version, compare_up_to: int
    ) -> bool:
        return (
            other_version.epoch == self._version.epoch
            and other_version.release[:compare_up_to]
            == self._version.release[:compare_up_to]
        )

    @staticmethod
    def _version_is_all_numeric(version: str) -> bool:
        return all(c.isdigit() for c in version.split("."))


class Requirement:
    """Represents a dependency of a python module."""

    __slots__ = ("name", "rules")

    def __init__(self, name: str, version_rules: list[VersionRule]) -> None:
        self.name: str = name
        self.rules: list[VersionRule] = version_rules

    def __str__(self) -> str:
        return self.name + "".join(map(str, self.rules))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Requirement)
            and self.name == other.name
            and len(self.rules) == len(other.rules)
            and all(rule1 == rule2 for rule1, rule2 in zip(self.rules, other.rules))  # noqa: B905
        )

    def __hash__(self) -> int:
        return hash(self.name + "".join(str(r) for r in self.rules))

    def matches_installed_version(
        self, direct_reference_handler: Callable[[str, str], bool] | None = None
    ) -> bool:
        """Checks if the installed version of a package is compliant with all rules.

        :param version: To check against
        :direct_reference_handler: Callable taking first the input `version` and second
            the reference version that determines how direct references `@` are handled
        :raises ValueError: If `direct_reference_handler` is None and a
            direct refernce is encountered."""

        installed_version: str = get_module_version(self.name)

        return all(
            rule.version_is_compliant(installed_version, direct_reference_handler)
            for rule in self.rules
        )


def is_literal_operator(operator: Operators) -> bool:
    """Returns True when `operator` will use literal comparison.

    :param operator: To check
    :returns: True when literal comparison will be used"""
    return operator in (
        Operators.ARBITRARY_EQUALITY,
        Operators.DIRECT_REFERENCE,
    )


def parse_requirements_file(
    file_path: str, encoding: str = "utf-8"
) -> list[Requirement]:
    """Given a requirements file, returns a list of
    objects representing the dependencies.
    """
    with open(file_path, encoding=encoding) as fp:
        file_contents: str = fp.read()

    return parse_requirements(file_contents)


def parse_requirements(
    raw_requirements: str, ignore_based_on_env_marker: bool = True
) -> list[Requirement]:
    """Given contents of a requirements file, returns a list of
    objects representing the dependencies.

    If ignore_based_on_env_marker is true, will not include requirements
    that do not match env. Such as excluding "...;platform_system == 'Windows'"
    when running on Linux.
    """

    requirements: list[Requirement] = []

    # regex slipt on \n without previous \
    raw_requirements = raw_requirements.strip()
    for line in re.split(r"(?<=[^\\])\s*\n", raw_requirements):
        split_line: list[str] = line.split(";")

        if ignore_based_on_env_marker and len(split_line) > 1:
            env_markers: str = split_line[1]
            env_valid: bool = parse_env_marker(env_markers)

            if not env_valid:
                continue

        requirement_line: str = split_line[0]

        requirement: Requirement = parse_requirement(requirement_line)
        requirements.append(requirement)

    return requirements


def parse_requirement(requirement: str) -> Requirement:
    """Given a single line of a requirements file, returns
    data parsed into a Requirements object.
    """
    requirement = re.sub(r"(\s+|\\\s*\n)", "", requirement)

    search_result = re.search(_REQUIREMENT_RE, requirement, re.IGNORECASE)

    if search_result is None:
        raise ValueError(f"Invalid requirement {requirement}")

    name: str = search_result.group(1)
    unparsed_rules: str = search_result.group(2)

    version_rules: list[VersionRule] = make_version_rules(unparsed_rules)

    return Requirement(name, version_rules)


def make_version_rules(unparsed_rules: str) -> list[VersionRule]:
    """Parses string of rules into list of VersionRule."""
    if unparsed_rules[0] == Operators.DIRECT_REFERENCE:
        return [VersionRule(Operators.DIRECT_REFERENCE, unparsed_rules[1:])]

    split_version_rules: list[tuple[Operators, str]] = re.findall(
        _OPERATOR_WITH_VERSION_RE, unparsed_rules, flags=re.IGNORECASE
    )

    return [VersionRule(operator, version) for operator, version in split_version_rules]


def parse_env_marker(env_markers: str) -> bool:
    """Parses an env marker with pep345 rules.

    https://peps.python.org/pep-0345/

    Returns True if marker is valid in current env.
    """

    for env_marker in re.split(r" (or|and) ", env_markers):
        search_result = re.search(_ENV_MARKER_RE, env_marker, re.IGNORECASE)

        if search_result is None:
            raise ValueError(f"Invalid env marker {env_marker}")

        try:
            left: str = env_marker_expr_to_value(search_result.group(1).strip())
            right: str = env_marker_expr_to_value(search_result.group(3).strip())
        except ValueError:
            continue  # TODO: Handle all env var and no longer catch here

        operator: str = search_result.group(2)

        env_valid: bool

        match operator:
            case EnvMarkerOperators.EQUALS:
                env_valid = left == right
            case EnvMarkerOperators.NOT_EQUALS:
                env_valid = left != right
            case EnvMarkerOperators.IN:
                env_valid = left in right
            case EnvMarkerOperators.NOT_IN:
                env_valid = left not in right

        if not env_valid:
            return False

    return True


def env_marker_expr_to_value(expr: str) -> str:
    """Given the expr as part of an env marker,
    update to its value in the current env such as
    'platform_system' -> 'Windows'.
    """

    if len(expr) > 1 and expr[0] == expr[-1] and expr[0] in "'\"" and expr[-1] in "'\"":
        # its wrapped in quotes, so its a string
        return expr[1:-1]

    match expr:
        case EnvMarkerExprs.PLATFORM_SYS:
            return platform.system()
        case _:
            raise ValueError(f"Unknown env var {expr}")
