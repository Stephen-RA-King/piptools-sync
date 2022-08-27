# Core Library modules
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_find_yaml_config_file() -> None:
    result = piptools_sync.find_yaml_config_file()
    file = result.stem
    assert file == ".pre-commit-config"
