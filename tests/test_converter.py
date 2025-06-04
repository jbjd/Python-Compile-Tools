import pytest

from personal_compile_tools.converters import version_str_to_tuple, version_tuple_to_str


@pytest.mark.parametrize(
    "version,expected_output",
    [((1, 2, 3), "1.2.3"), ((7,), "7")],
)
def test_version_tuple_to_str(version: tuple[int, ...], expected_output: str):
    """Should return correct tuple given a version str"""

    assert version_tuple_to_str(version) == expected_output


@pytest.mark.parametrize(
    "version,expected_output",
    [("1.2.3", (1, 2, 3)), ("7", (7,))],
)
def test_version_str_to_tuple(version: str, expected_output: tuple[int, ...]):
    """Should return correct tuple given a version str"""

    assert version_str_to_tuple(version) == expected_output


@pytest.mark.parametrize("version", ["", "1.a.5"])
def test_version_str_to_tuple_bad_input(version: str):
    """Should raise ValueError when given bad input"""

    with pytest.raises(ValueError):
        version_str_to_tuple(version)
