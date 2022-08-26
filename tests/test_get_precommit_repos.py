# Core Library modules
import os
from typing import Any

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync


def test_get_precommit_repos(mock_get_precommit_repos: Any) -> None:
    x = piptools_sync.get_precommit_repos()
    assert x == [["https://github.com/pre-commit/mirrors-mypy", "mypy"]]
