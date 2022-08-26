# Core Library modules
from pathlib import Path
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync


def pytest_configure() -> None:
    pytest.TEST_DIR = Path(__file__).parent


@pytest.fixture
def mock_get_precommit_repos(monkeypatch: Any) -> None:
    def mock_get_precommitrepos() -> list[list]:
        repos = [["https://github.com/pre-commit/mirrors-mypy", "mypy"]]
        return repos

    monkeypatch.setattr(piptools_sync, "get_precommit_repos", mock_get_precommitrepos)
