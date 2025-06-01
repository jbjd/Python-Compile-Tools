import os

import pytest

from personal_compile_tools.requirements import (
    Requirement,
    parse_requirement,
    parse_requirements_file,
    VersionRule,
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

    assert requirements[1] == Requirement("other", [VersionRule("===", "7.0.8")])


@pytest.mark.parametrize(
    "bad_input", ["-cannot-start-with-dash==1.0.0", "not_pep440==1.0.4-snapshot"]
)
def test_parse_requirement_bad_input(bad_input: str):
    """Should raise ValueError due to invalid requirement entry"""

    with pytest.raises(ValueError):
        parse_requirement(bad_input)
