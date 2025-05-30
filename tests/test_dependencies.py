from unittest.mock import patch

from personal_compile_tools.dependencies import Dependency

_MODULE_NAME: str = "personal_compile_tools.dependencies"


def test_matches_installed_version():
    """Should return correct bool given OS native response code"""

    PACKAGE: str = "some_package"
    VERSION: str = "1.2.3.4"

    dependency = Dependency(PACKAGE, VERSION)

    with patch(f"{_MODULE_NAME}.get_module_version", side_effect=lambda _: VERSION):
        assert dependency.matches_installed_version()

    with patch(
        f"{_MODULE_NAME}.get_module_version", side_effect=lambda _: VERSION + ".5"
    ):
        assert not dependency.matches_installed_version()
