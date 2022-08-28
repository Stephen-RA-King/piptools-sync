# Core Library modules
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_yaml_to_dict() -> None:
    test_file = TEST_DIR / "test.yaml"
    result = piptools_sync.yaml_to_dict(test_file)
    assert result == {
        "https://github.com/commitizen-tools/commitizen": "2.32.2",
        "https://github.com/psf/black": "22.6.0",
    }
