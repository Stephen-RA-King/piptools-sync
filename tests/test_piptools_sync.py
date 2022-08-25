"""Tests for package cookietest.py
To use tests either:
    1 - Use pip to install package as "editable"
            pip install -e .
    2 - Import pathmagic.py to enable tests to find the package
"""
# Core Library modules
import os
from pathlib import Path

# First party modules
from piptools_sync import tryout

TEST_DIR = Path(__file__).parent


def test_utility_find_file_path() -> None:
    result = tryout._utility_find_file_path(r"requirements\development.txt")
    assert os.path.relpath(TEST_DIR, result) == r"..\..\tests"
    assert os.path.relpath(result, TEST_DIR) == r"..\requirements\development.txt"
