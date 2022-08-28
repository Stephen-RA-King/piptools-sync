# Core Library modules
import shutil
from pathlib import Path
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR
ROOT_DIR = piptools_sync.ROOT_DIR


def test_get_requirement_versions() -> None:
    req_file = ROOT_DIR / "tests" / "reqs" / "dev.txt"
    result = piptools_sync.get_requirement_versions(
        req_file,
        [
            "click",
        ],
    )

    major, minor, patch = result["click"].split(".")
    assert int(major) >= 8
