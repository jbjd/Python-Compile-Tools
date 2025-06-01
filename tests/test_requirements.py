import os

from personal_compile_tools.requirements import Requirement, parse_requirements_file
from tests.conftest import EXAMPLE_FOLDER

_MODULE_NAME: str = "personal_compile_tools.requitements"


def test_parse_requirements_file():
    requirements: list[Requirement] = parse_requirements_file(
        os.path.join(EXAMPLE_FOLDER, "requirements.txt")
    )

    assert len(requirements) == 1

    requirement = requirements[0]

    assert requirement.name == "some_module"
    assert len(requirement.version_rules) == 2

    assert requirement.version_rules[0].operator == ">="
    assert requirement.version_rules[0].raw_version == "1.2.3"

    assert requirement.version_rules[1].operator == "<="
    assert requirement.version_rules[1].raw_version == "2.0.0"
