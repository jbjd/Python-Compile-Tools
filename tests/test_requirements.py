import os

import pytest

from personal_compile_tools.requirements import (
    Requirement,
    VersionRule,
    parse_requirement,
    parse_requirements_file,
)
from tests.conftest import EXAMPLE_FOLDER


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
