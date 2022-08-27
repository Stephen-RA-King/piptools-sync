# Core Library modules
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_generate_db(
    mock_get_precommit_repos: Any, mock_get_latest_pypi_repo_version: Any
) -> None:
    result = piptools_sync.generate_db()
    assert result == {"https://github.com/pre-commit/mirrors-mypy": "mypy"}
