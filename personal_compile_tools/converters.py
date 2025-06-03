"""Functions to convert. Currently focused on versions in the form x.y.z"""


def version_tuple_to_str(version: tuple[int, ...]) -> str:
    """Given a tuple of ints (x,y,z),
    returns them as a string "x.y.z" """
    return ".".join(map(str, version))


def version_str_to_tuple(version: str) -> tuple[int, ...]:
    """Given a string of x.y.z where all values are "." or numeric,
    returns them as a tuple (x,y,z)"""
    return tuple(map(int, version.split(".")))
