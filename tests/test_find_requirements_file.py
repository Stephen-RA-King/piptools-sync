# Core Library modules
import shutil
from pathlib import Path
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_find_requirements_file(monkeypatch: pytest) -> None:
    tmp_requirement = TEST_DIR / "req.txt"
    monkeypatch.setattr(piptools_sync, "ROOT_REQUIREMENT", tmp_requirement)
    result = piptools_sync.find_requirements_file()
    assert "".join([result.stem, result.suffix]) == "dev.txt"
