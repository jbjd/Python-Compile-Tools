"""Operators that are legal in requirement files"""

from enum import StrEnum


class Operators(StrEnum):
    EQUALS: str = "=="
    NOT_EQUALS: str = "!="
    GT: str = ">"
    GT_OR_EQUALS: str = ">="
    LT: str = "<"
    LT_OR_EQUALS: str = "<="
    COMPATIBLE: str = "~="
    ARBITRARY_EQUALITY: str = "==="
    DIRECT_REFERENCE: str = "@"


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
