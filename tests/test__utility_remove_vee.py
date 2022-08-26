# Core Library modules
import os

# Third party modules
import pytest

# First party modules
from piptools_sync import piptools_sync

TEST_DIR = pytest.TEST_DIR


def test_utility_remove_vee() -> None:
    assert piptools_sync._utility_remove_vee("0.1.0") == "0.1.0"
    assert piptools_sync._utility_remove_vee("v0.1.0") == "0.1.0"
    assert piptools_sync._utility_remove_vee("V0.1.0") == "0.1.0"
    assert piptools_sync._utility_remove_vee("v1.0") == "1.0"
    assert piptools_sync._utility_remove_vee("V1.0") == "1.0"
