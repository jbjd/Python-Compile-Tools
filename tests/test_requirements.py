import os

from personal_compile_tools.requirements import (
    Requirement,
    parse_requirements_file,
    VersionRule,
)
from tests.conftest import EXAMPLE_FOLDER

_MODULE_NAME: str = "personal_compile_tools.requitements"


def test_parse_requirements_file():
    """Should read a requirements file, handle backslash, and correctly parse it"""

    requirements: list[Requirement] = parse_requirements_file(
        os.path.join(EXAMPLE_FOLDER, "requirements.txt")
    )

    assert len(requirements) == 2

    assert requirements[0] == Requirement(
        "some_module", [VersionRule(">=", "1.2.3"), VersionRule("<=", "2.0.0")]
    )

    assert requirements[1] == Requirement("other", [VersionRule("===", "7.0.8")])


# def test_parse_requirement():
#     """Should parse a single line of """
