"""Tests for the requirements module."""

import os
import warnings
from unittest.mock import patch

import pytest

from personal_compile_tools.requirement_operators import Operators
from personal_compile_tools.requirements import (
    PreSegmentType,
    Requirement,
    VersionLiteral,
    VersionPep440,
    VersionRule,
    construct_pep440_version,
    make_version,
    normalize_version,
    parse_env_marker,
    parse_requirement,
    parse_requirements_file,
    version_is_pep440_compliant,
)
from tests.conftest import REQUIREMENTS_FOLDER

_MODULE_NAME = "personal_compile_tools.requirements"


def test_parse_requirements_file():
    """Should read a requirements file, handle backslash, and correctly parse it"""

    with patch(f"{_MODULE_NAME}.platform.system", lambda: "Windows"):
        requirements: list[Requirement] = parse_requirements_file(
            os.path.join(REQUIREMENTS_FOLDER, "requirements.txt")
        )

        assert len(requirements) == 3

        assert requirements[0] == Requirement(
            "some_module",
            [
                VersionRule(Operators.GT_OR_EQUALS, "1.2.3"),
                VersionRule(Operators.LT_OR_EQUALS, "2.0.0"),
            ],
        )

        assert requirements[1] == Requirement(
            "o", [VersionRule(Operators.EQUALS, "7.0.8")]
        )

        assert requirements[2] == Requirement(
            "dir_ref",
            [
                VersionRule(
                    Operators.DIRECT_REFERENCE,
                    "git+https://github.com/jbjd/Compile-Tools@v1.0.0",
                )
            ],
        )


def test_parse_env_marker():
    """Should return True if env markers valid for current env"""
    env_marker: str = ' platform_system =="Windows"'

    with patch(f"{_MODULE_NAME}.platform.system", lambda: "Windows"):
        assert parse_env_marker(env_marker)

    with patch(f"{_MODULE_NAME}.platform.system", lambda: "Linux"):
        assert not parse_env_marker(env_marker)


def test_parse_env_marker_bad_input():
    """Should ignore invalid env markers"""
    env_marker: str = ' not_env_marker =="Windows"'

    assert parse_env_marker(env_marker)


@pytest.mark.parametrize(
    "bad_input",
    [
        "-cannot-start-with-dash==1.0.0",
        "not_pep440==1.0.4-snapshot",
        "invalid_op_plus_version~=7",
        "invalid_op_with_fuzzy~=7.1.*",
    ],
)
def test_parse_requirement_bad_input(bad_input: str):
    """Should raise ValueError due to invalid requirement entry"""

    with pytest.raises(ValueError):
        parse_requirement(bad_input)


@pytest.mark.parametrize(
    ("operator", "version"),
    [
        ("=", "1.2.3"),  # = is not an operator
        (">=", "1.2.*"),  # .* can only be used with == or !=
    ],
)
def test_version_rule_bad_input(operator: str, version: str):
    """Should raise ValueError when release version not parsed"""

    with pytest.raises(ValueError):
        VersionRule(operator, version)


def test_construct_pep440_version_bad_input():
    """Should raise ValueError when illegal input value combinations present"""

    # Specifies pre segment type without a value
    with pytest.raises(ValueError):
        construct_pep440_version((1, 2, 3), PreSegmentType.ALPHA)

    # Specifies no pre segment type, but does specify  a value
    with pytest.raises(ValueError):
        construct_pep440_version((1, 2, 3), pre_segment=3)


def test_bad_comparison():
    """Should raise ValueError when literal version is compared < or >"""

    with pytest.raises(ValueError):
        _ = VersionLiteral("asdf") > VersionLiteral("1.9")

    with pytest.raises(ValueError):
        _ = VersionLiteral("asdf") <= VersionLiteral("1.9")


def test_bad_compare_parts_up_to():
    """Should raise ValueError when compare_parts_up_to called on literal version"""

    with pytest.raises(ValueError):
        VersionLiteral("asdf").compare_parts_up_to(VersionLiteral("asdf"), 1)


@pytest.mark.parametrize(
    ("raw_version", "is_literal", "expected_count"),
    [("asdf", True, 0), ("1.2.3.4", False, 4)],
)
def test_get_version_parts_len(raw_version: str, is_literal: bool, expected_count: int):
    """Should return correct number of parts given type of version"""
    version = make_version(raw_version, is_literal)

    if is_literal:
        with pytest.raises(ValueError):
            version.get_version_parts_len()
    else:
        assert version.get_version_parts_len() == expected_count


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", True),
        ("1", "1.0", True),
        ("1alpha5", "1.0a5", True),
        ("1beta1", "1.0a1", False),
        ("1.post1", "1.dev1", False),
        ("1.4.0.1", "1.4", False),
        ("1.4.5", "1.4.8", False),
    ],
)
def test_equals_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is equal to version"""

    rule = VersionRule(Operators.EQUALS, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", False),
        ("1", "1.0", False),
        ("1.4.0.1", "1.4", True),
        ("1.4.5", "1.4.8", True),
        ("1.9a1", "1.9.0alpha1", False),
    ],
)
def test_not_equals_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is not equal to version"""

    rule = VersionRule(Operators.NOT_EQUALS, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.8", True),
        ("1.4.5", "1.4.8.6", True),
        ("1.4.5", "1.4.5", True),
        ("1.4", "1.4.5", True),
        ("1.4.5", "1.5.4", False),
        ("1.4.5", "1.4.4", False),
        ("1.4.5", "2.0.0", False),
        ("1.4.5", "1.4.5a1", False),
        ("2.2.post3", "2.3", True),
        ("2.2rc4", "2.2.post3", True),
        ("2.2rc4", "2.1.post3", False),
    ],
)
def test_compatible_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version compatible with version rule"""

    rule = VersionRule(Operators.COMPATIBLE, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("operator", "version", "installed_version", "expected_compliance"),
    [
        (Operators.EQUALS, "1.4.*", "1.4.5", True),
        (Operators.EQUALS, "1.4.*", "1.4.5.1", True),
        (Operators.EQUALS, "1.4.*", "1.0.5", False),
        (Operators.EQUALS, "1.4.5.*", "1.4", False),
        (Operators.EQUALS, "1.4.5.*", "1.4.5", True),
        (Operators.EQUALS, "1.0.0.0.*", "1.0.0.0.6", True),
        (Operators.EQUALS, "1.0.0.0.*", "1.0.0.0.0", True),
        (Operators.EQUALS, "1.0.0.0.*", "1.0.0.6", False),
    ],
)
def test_fuzzy_match(
    operator: str,
    version: str,
    installed_version: str,
    expected_compliance: bool,
):
    """Should return correct bool when fuzzy matching"""

    rule = VersionRule(operator, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", False),
        ("1", "1.0", False),
        ("1.4", "1.4.0.1", True),
        ("1.4.8", "1.4.5", False),
        ("1.9a1", "1.9.0a2", True),
        ("1.9b1", "1.9.0b2", True),
        ("1.9.0c1", "1.9", True),
        ("1.9.dev1", "1.9", True),
        ("1.9.dev1", "1.9.dev2", True),
        ("1.9c1.post2.dev1", "1.9c1.dev2", False),
        ("1.9c1.post2.dev1", "1.9c1", False),
        ("1.9.post2.dev1", "1.9c1.dev2", False),
    ],
)
def test_greater_than_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is greater than version"""

    rule = VersionRule(Operators.GT, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", True),
        ("2.post1.dev2", "2.post1.dev0", False),
        ("2.post1.dev2", "2.post2.dev0", True),
    ],
)
def test_greater_than_or_equal_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is greater than version"""

    rule = VersionRule(Operators.GT_OR_EQUALS, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", False),
        ("1.3", "1.2", True),
        ("7.8.9b1.post2", "7.8.9.dev1", False),
        ("7.8.9b1.post2", "7.8.9a0", True),
    ],
)
def test_less_than_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is greater than version"""

    rule = VersionRule(Operators.LT, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", True),
        ("1.dev6", "1.2.dev5", False),
        ("4.3b5.post2", "4.3b5.post2.dev9", True),
    ],
)
def test_less_than_or_equal_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is greater than version"""

    rule = VersionRule(Operators.LT_OR_EQUALS, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("1.4.5", "1.4.5", True),
        ("any-comboOf5tuff", "any-comboOf5tuff", True),
        ("123", "132", False),
    ],
)
def test_arbitrary_equality_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is greater than version"""

    rule = VersionRule(Operators.ARBITRARY_EQUALITY, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    ("version", "installed_version", "expected_compliance"),
    [
        ("git+https://github.com/pypa/pip.git@7921be1", "1.4.5", True),
        ("file:///c:/path/to/a/file", "1.4.5", False),
    ],
)
def test_direct_reference_operator(
    version: str, installed_version: str, expected_compliance: bool
):
    """Should return correct bool if installed version is greater than version."""

    rule = VersionRule(Operators.DIRECT_REFERENCE, version)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "Can't verify if source at * ")
        assert (
            rule.version_is_compliant(installed_version, expected_compliance)
            is expected_compliance
        )


@pytest.mark.parametrize(
    ("version", "expected_compliance"),
    [
        ("1.4.5", True),
        ("1alpha2.dev6", True),
        ("8.9beta4.post5.dev7", True),
        ("8.9c6", True),
        (".9c6", False),
        ("8beta4rc4.dev6", False),
        ("4.3b5.post2-", False),
    ],
)
def test_version_is_pep440_compliant(version: str, expected_compliance: bool):
    """Should return correct bool if installed version is greater than version."""

    assert version_is_pep440_compliant(version) is expected_compliance


@pytest.mark.parametrize(
    ("installed_version", "expected_compliance"),
    [("1.4.5", True), ("2.0.0", False), ("1.2.3", True), ("1.2.2", False)],
)
def test_matches_installed_version(installed_version: str, expected_compliance: bool):
    """Should ensure installed version complies with all rules."""
    requirement = Requirement(
        "asdf", [VersionRule(">=", "1.2.3"), VersionRule("<", "2.0.0")]
    )

    with patch(f"{_MODULE_NAME}.get_module_version", lambda _: installed_version):
        assert requirement.matches_installed_version() is expected_compliance


@pytest.mark.parametrize(
    ("name", "operator_and_version"),
    [
        ("asdf", [(Operators.EQUALS, "1.2.3a3.post1.dev6")]),
        ("asdf", [(Operators.EQUALS, "1.2.*")]),
        (
            "test-name",
            [
                (Operators.GT_OR_EQUALS, "1"),
                (Operators.LT, "2"),
            ],
        ),
    ],
)
def test_as_str(name: str, operator_and_version: list[tuple[str, str]]):
    """Should ensure installed version complies with all rules."""
    as_class = Requirement(name, [VersionRule(op, v) for op, v in operator_and_version])

    expected_result: str = name + "".join(op + v for op, v in operator_and_version)

    assert str(as_class) == expected_result


@pytest.mark.parametrize(
    ("input_version", "expected_version"),
    [
        ("1-alpha2-post3-dev4", "1a2.post3.dev4"),
        ("6.08_beta0_post1_dev2", "6.8b0.post1.dev2"),
        ("1.C2post1dev2", "1rc2.post1.dev2"),
    ],
)
def test_normalize_version(input_version: str, expected_version: str):
    """Should ensure installed version complies with all rules."""

    assert normalize_version(input_version) == expected_version


def test_hashing():
    """Should hash classes without issue."""

    assert hash(VersionLiteral("a"))
    assert hash(VersionPep440("1"))
    assert hash(VersionRule("==", "1"))
    assert hash(Requirement("a", []))
