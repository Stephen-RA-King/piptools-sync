# Core Library modules
import shutil
from pathlib import Path
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_find_requirements_file() -> None:
    result = piptools_sync.get_installed_version("setuptools")
    major, minor, patch = result.split(".")
    assert int(major) >= 65
