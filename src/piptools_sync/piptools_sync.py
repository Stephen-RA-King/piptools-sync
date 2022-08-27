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

logger.debug(f"ROOT_DIR: {'':20}{ROOT_DIR}\n" f"MAPPING_FILE: {'':20}{MAPPING_FILE}\n")


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

    logger.debug("starting **** _utility_find_file_path ****")
    result_list = sorted(Path(ROOT_DIR).glob(partial_path))
    logger.debug(f"result_list: {result_list}")
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
    version_updated: str
        Version numbers as a string without a prefixing letter.
    """

    logger.debug("starting **** _utility_remove_vee ****")
    version_updated = ""
    vee, *rest = version  # type:ignore
    if vee in ["v", "V"]:  # type:ignore
        version_updated = "".join(rest)  # type:ignore
    logger.debug(f"{version} returned {version_updated}")
    return version_updated


def get_precommit_repos() -> list[list]:
    """Get a list of repos from pre-commit.com using the selected filters.

    # TODO: possibly refactor data structure to dictionary at later stage with the
        following structure dict{key: value and key: [list]} :

    Returns
    -------
    pyrepos : list[list]
        data structure: [['html repo name': 'str'], ['html repo name': 'str'], ... ]
        e.g. [['https://github.com/pre-commit/mirrors-mypy', 'mypy']]
    """

    logger.debug("starting **** get_precommit_repos ****")
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
    logger.debug(f"Number of pre-commit hooks found: {len(pyrepos)}")
    return pyrepos


def get_latest_github_repo_version(url_src: str) -> Union[str, int]:
    """Given a repo URL, return the latest version from GitHub utilizing API.

    Parameters
    ----------
    url_src : str
        The url of the GitHub repository.

    Returns
    -------
    version : str
        the latest repository version extracted from the API.
    0 :
        If the version cannot be found.

    Raises
    ------
    SystemExit:
        if requests.get() operations fails for any reason.
    """

    logger.debug("starting **** get_latest_github_repo_version ****")
    url_int = url_src.replace("https://github.com/", "https://api.github.com/repos/")
    dst_url = "".join([url_int, "/releases/latest"])
    headers = {"Accept": "application/vnd.github+json"}
    try:
        r = requests.get(dst_url, headers=headers)
        data = r.json()
        version = data.get("name", 0)
        if not version:
            logger.debug(f"0 - for {url_src}")
            return 0
        else:
            logger.debug(f"{version} - for {url_src}")
            return version
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from None


def get_latest_pypi_repo_version(name: str) -> Union[str, int]:
    """Given a repository name , find the latest version utilizing PyPI API.

    Parameters
    name : str
        Supplied project name. This is not the URL.

    Returns
    version : str
        The latest repository version.

    0 :
        Indicates the repository was not found.

    Raises
    SystemExit:
        if requests.get() operations fails for any reason.
    """

    logger.debug("starting **** get_precommit_repos ****")
    int_url = "https://pypi.org/pypi/<project>/json"
    dst_url = int_url.replace("<project>", name)
    headers = {"Accept": "application/json"}
    try:
        r = requests.get(dst_url, headers=headers)
        data = r.json()
        if data.get("message", 0) == "Not Found":
            logger.debug(f"0 - for {name}")
            return 0
        else:
            version = data["info"]["version"]
            logger.debug(f"{version} - for {name}")
            return version
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from None
