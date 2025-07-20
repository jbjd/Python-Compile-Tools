"""Operators that are legal in requirement files"""

from enum import StrEnum


class Operators(StrEnum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GT = ">"
    GT_OR_EQUALS = ">="
    LT = "<"
    LT_OR_EQUALS = "<="
    COMPATIBLE = "~="
    ARBITRARY_EQUALITY = "==="
    DIRECT_REFERENCE = "@"


VALID_OPERATORS: list[str] = [
    Operators.EQUALS,
    Operators.NOT_EQUALS,
    Operators.GT,
    Operators.GT_OR_EQUALS,
    Operators.LT,
    Operators.LT_OR_EQUALS,
    Operators.COMPATIBLE,
    Operators.ARBITRARY_EQUALITY,
    Operators.DIRECT_REFERENCE,
]


class EnvMarkerOperators(StrEnum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    IN = " in "
    NOT_IN = " not in "


VALID_ENV_MARKER_OPERATORS: list[str] = [
    EnvMarkerOperators.EQUALS,
    EnvMarkerOperators.NOT_EQUALS,
    EnvMarkerOperators.IN,
    EnvMarkerOperators.NOT_IN,
]


class EnvMarkerExprs(StrEnum):
    PLATFORM_SYS = "platform_system"
