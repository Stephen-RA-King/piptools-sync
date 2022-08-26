"""A pre-commit utility plugin to verify requirement versions determined by
pip-tools are utilized by pre-commit
"""
# TODO: add logging
# TODO: add docstrings
# TODO: add mypy types
# TODO: create tests
# TODO: increase indentation on yaml write

# Core Library modules
import json
import os
import time
from pathlib import Path
from typing import Any, Union

# Third party modules
import pkg_resources  # type:ignore
import requests  # type:ignore
import yaml  # type:ignore
from tqdm import tqdm

# Local modules
from . import MAPPING_FILE, ROOT_DIR, logger, toml_config

logger.debug(f"root directory defined as {ROOT_DIR}")
logger.debug(f"mapping file path: {MAPPING_FILE}")

PRECOMMIT_CONFIG_FILE = ".pre-commit-config.yaml"
PRECOMMIT_REPOS_URL = "https://pre-commit.com/all-hooks.json"

# TODO: store the following in a settings.yaml file
ROOT_REQUIREMENT = ROOT_DIR / "requirements.txt"
REGEN_PERIOD = 604800  # one week
UPDATE_PC_YAML_FILE = True
PRECOMMIT_FILTERS = ["python", "toml"]
MANUAL_MAPPING = {
    "https://github.com/pre-commit/mirrors-autopep8": "autopep8",
    "https://github.com/pre-commit/mirrors-mypy": "mypy",
    "https://github.com/pre-commit/mirrors-yapf": "yapf",
    "https://github.com/FalconSocial/pre-commit-mirrors-pep257": "pep257",
}


def load_settings() -> None:
    config_result = [(bool(toml_config["APP"]["DEBUG"]))]


def _utility_find_file_path(partial_path: str) -> Union[Path, int]:
    """Given a partial file path, find the absolute file path for the file.

    Do a search from the project root matching a full absolute path containing
    the partial path as a substring.

    Parameters
    ----------
    partial_path : str
        A string representing a substring of the absolute path.

    Returns
    -------
    result_list : Path
        A pathlib type path object of the full absolute path.
    0 :
        Error condition indicates that no match was found.
    1 :
        Error condition indicates more than 1 match was found and is ambiguous.
    """

    result_list = sorted(Path(ROOT_DIR).glob(partial_path))
    if len(result_list) == 0:
        return 0
    elif len(result_list) > 1:
        return 1
    else:
        return result_list[0]


def _utility_remove_vee(version: str) -> str:
    """Return the supplied version number without a prefixing 'v' or 'V'.

    Parameters
    ----------
    version : str
        Version given may or may not have a prefixing letter.

    Returns
    -------
    version: str
        Version numbers as a string without a prefixing letter.
    """

    vee, *rest = version  # type:ignore
    if vee in ["v", "V"]:  # type:ignore
        version = "".join(rest)  # type:ignore
    return version


def get_precommit_repos() -> list[list]:
    """Get a list of repos from pre-commit.com using the selected filters.

    Returns
    -------
    pyrepos : list[list]
        data structure: [['html repo name': 'str'], ['html repo name': 'str'], ... ]
        e.g. [['https://github.com/pre-commit/mirrors-mypy', 'mypy']]
    """

    pyrepos = []
    r = requests.get(PRECOMMIT_REPOS_URL)
    data = r.json()
    for repo in data:
        sublist = [repo]
        for _, subrepo in enumerate(data[repo]):
            if subrepo["language"] in PRECOMMIT_FILTERS:
                sublist.append(subrepo["name"])
        if len(sublist) > 1:
            pyrepos.append(sublist)
    return pyrepos
