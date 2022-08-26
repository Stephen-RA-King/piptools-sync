# Core Library modules
import os

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_utility_find_file_path() -> None:
    result = piptools_sync._utility_find_file_path(r"requirements\development.txt")
    assert os.path.relpath(TEST_DIR, result) == r"..\..\tests"
    assert os.path.relpath(result, TEST_DIR) == r"..\requirements\development.txt"
    assert piptools_sync._utility_find_file_path("xx") == 0
    assert piptools_sync._utility_find_file_path("setup.*") == 1
