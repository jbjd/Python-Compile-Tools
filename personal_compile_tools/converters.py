"""Common converters."""


def version_tuple_to_str(version: tuple[int, ...]) -> str:
    """Converts version tuple (x,y) to string 'x.y'.

    :param version: Version tuple
    :returns: Version string
    """
    return ".".join(map(str, version))


def version_str_to_tuple(version: str) -> tuple[int, ...]:
    """Converts version string 'x.y' to tuple (x,y).

    :param version: Version string
    :returns: Version tuple
    """
    return tuple(map(int, version.split(".")))
