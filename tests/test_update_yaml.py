# Core Library modules
import shutil
from pathlib import Path
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_yaml_to_dict() -> None:
    src_file = TEST_DIR / "test.yaml"
    dst_file = TEST_DIR / "dst.yaml"

    shutil.copy(src_file, dst_file)

    piptools_sync.update_yaml(dst_file, "https://github.com/psf/black", "23.0.0")

    result = piptools_sync.yaml_to_dict(dst_file)
    assert result == {
        "https://github.com/commitizen-tools/commitizen": "2.32.2",
        "https://github.com/psf/black": "23.0.0",
    }

    dst_file.unlink()
