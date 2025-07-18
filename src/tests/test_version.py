"""Tests for the version."""

from src import tinycta


def test_version():
    """Test if the version of the tinycta library is defined.

    This function checks that the version constant in the tinycta module is
    not None, ensuring that the version information is properly assigned.

    Raises:
        AssertionError: If the version constant is None.

    """
    assert tinycta.__version__ is not None
