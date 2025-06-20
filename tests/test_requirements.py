import os
from typing import Literal
from unittest.mock import patch

import pytest

from personal_compile_tools.requirements import (
    Requirement,
    VersionPep440,
    VersionRule,
    parse_requirement,
    parse_requirements_file,
    version_is_pep440_compliant,
)
from tests.conftest import EXAMPLE_FOLDER

_MODULE_NAME = "personal_compile_tools.requirements"


def test_parse_requirements_file():
    """Should read a requirements file, handle backslash, and correctly parse it"""

    requirements: list[Requirement] = parse_requirements_file(
        os.path.join(EXAMPLE_FOLDER, "requirements.txt")
    )

    assert len(requirements) == 2

    assert requirements[0] == Requirement(
        "some_module", [VersionRule(">=", "1.2.3"), VersionRule("<=", "2.0.0")]
    )

    assert requirements[1] == Requirement("other", [VersionRule("==", "7.0.8")])


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
    "operator,version",
    [
        ("=", "1.2.3"),  # = is not an operator
        (">=", "1.2.*"),  # .* can only be used with == or !=
    ],
)
def test_version_rule_bad_input(operator: str, version: str):
    """Should raise ValueError when release version not parsed"""

    with pytest.raises(ValueError):
        VersionRule(operator, version)


def test_bad_comparison():
    """Should raise ValueError when release version not parsed"""

    with pytest.raises(ValueError):
        VersionPep440("asdf", is_literal=True) > VersionPep440("1.9")


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    COMPATIBLE_OP = "~="

    rule = VersionRule(COMPATIBLE_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    EQUALS_OP = "=="

    rule = VersionRule(EQUALS_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    NOT_EQUALS_OP = "!="

    rule = VersionRule(NOT_EQUALS_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "operator,version,installed_version,expected_compliance",
    [
        ("==", "1.4.*", "1.4.5", True),
        ("==", "1.4.*", "1.4.5.1", True),
        ("==", "1.4.*", "1.0.5", False),
        ("==", "1.4.5.*", "1.4", False),
        ("==", "1.4.5.*", "1.4.5", True),
    ],
)
def test_fuzzy_match(
    operator: Literal["==", "!="],
    version: str,
    installed_version: str,
    expected_compliance: bool,
):
    """Should return correct bool when fuzzy matching"""

    rule = VersionRule(operator, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    GT_OP = ">"

    rule = VersionRule(GT_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    GT_OR_EQUAL_OP = ">="

    rule = VersionRule(GT_OR_EQUAL_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    LT_OP = "<"

    rule = VersionRule(LT_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    LT_OR_EQUAL_OP = "<="

    rule = VersionRule(LT_OR_EQUAL_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,installed_version,expected_compliance",
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

    ARBITRARY_EQUALITY_OP = "==="

    rule = VersionRule(ARBITRARY_EQUALITY_OP, version)

    assert rule.version_is_compliant(installed_version) is expected_compliance


@pytest.mark.parametrize(
    "version,expected_compliance",
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
    """Should return correct bool if installed version is greater than version"""

    assert version_is_pep440_compliant(version) is expected_compliance


@pytest.mark.parametrize(
    "installed_version,expected_compliance",
    [("1.4.5", True), ("2.0.0", False), ("1.2.3", True), ("1.2.2", False)],
)
def test_matches_installed_version(installed_version: str, expected_compliance: bool):
    """Should ensure installed version complies with all rules"""
    requirement = Requirement(
        "asdf", [VersionRule(">=", "1.2.3"), VersionRule("<", "2.0.0")]
    )

    with patch(f"{_MODULE_NAME}.get_module_version", lambda _: installed_version):
        assert requirement.matches_installed_version() is expected_compliance


@pytest.mark.parametrize(
    "requirememnt,expected_str",
    [
        (Requirement("asdf", [VersionRule("==", "1.2.3.post1")]), "asdf==1.2.3.post1"),
        (Requirement("asdf", [VersionRule("==", "1.2.*")]), "asdf==1.2.*"),
        (
            Requirement("test-name", [VersionRule(">=", "1"), VersionRule("<", "2")]),
            "test-name>=1<2",
        ),
    ],
)
def test_as_str(requirememnt: Requirement, expected_str: str):
    """Should ensure installed version complies with all rules"""
    assert str(requirememnt) == expected_str
