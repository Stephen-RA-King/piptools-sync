#!/usr/bin/env python3
"""A pre-commit plugin to sync versions from pip-tools to pre-commit."""

# Core Library modules
import json
import os
import time
from importlib.metadata import PackageNotFoundError, version as ver
from importlib.resources import as_file
from pathlib import Path
from typing import Any, Union

# Third party modules
import requests
import yaml
from tqdm import tqdm

# Local modules
from . import MAPPING_FILE, ROOT_DIR, logger, toml_config

PRECOMMIT_CONFIG_FILE = ".pre-commit-config.yaml"
PRECOMMIT_REPOS_URL = "https://pre-commit.com/all-hooks.json"
ROOT_REQUIREMENT = ROOT_DIR / "requirements.txt"
REGEN_PERIOD = 15724800  # 6 months
UPDATE_PC_YAML_FILE = True
PRECOMMIT_FILTERS = ["python", "toml"]
MANUAL_MAPPING = {
    "https://github.com/pre-commit/mirrors-autopep8": "autopep8",
    "https://github.com/pre-commit/mirrors-mypy": "mypy",
    "https://github.com/pre-commit/mirrors-yapf": "yapf",
    "https://github.com/FalconSocial/pre-commit-mirrors-pep257": "pep257",
}


def load_settings() -> None:
    """Get the configuration settings from the toml file."""
    debug_config = [(bool(toml_config["APP"]["DEBUG"]))]  # noqa
    if not debug_config:
        logger.disabled = True


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
    logger.debug("attempting to find: %s", partial_path)
    result_list = sorted(Path(ROOT_DIR).glob(partial_path))
    logger.debug("result_list: %s", result_list)
    if len(result_list) == 0:
        logger.debug("Error - no files found: %s", result_list)
        return 0
    elif len(result_list) > 1:
        logger.debug("Error - more than one file found: %s", result_list)
        return 1
    else:
        logger.debug("file found: %s", result_list)
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

    Notes
    -----
    v3.9 introduces str.removeprefix() method. Usage with str.startswith((x, y...))
    method possible but less succinct as removeprefix does not accept a tuple.
    """
    vee, *rest = version  # type:ignore
    if vee in ["v", "V"]:  # type:ignore
        version = "".join(rest)  # type:ignore
        logger.debug("removed prefix 'v' - returned %s", version)
    return version


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
    pyrepos = []
    r = requests.get(PRECOMMIT_REPOS_URL, timeout=15)
    data = r.json()
    for repo in data:
        sublist = [repo]
        for _, subrepo in enumerate(data[repo]):
            if subrepo["language"] in PRECOMMIT_FILTERS:
                sublist.append(subrepo["name"])
        if len(sublist) > 1:
            pyrepos.append(sublist)
    logger.debug("Number of pre-commit hooks found: %s", len(pyrepos))
    return pyrepos


def get_precommit_repos_2() -> dict:
    """Get a list of repos from pre-commit.com using the selected filters.

    Returns
    -------
    pyrepos : dict
        data structure: [['html repo name': 'str'], ['html repo name': 'str'], ... ]
        e.g. {'https://github.com/pre-commit/mirrors-mypy': 'mypy', ...}
    """
    pyrepos = {}
    r = requests.get(PRECOMMIT_REPOS_URL, timeout=15)
    data = r.json()
    for repo in data:
        language = data[repo][0]["language"]
        subrepos = len(data[repo])
        if language in PRECOMMIT_FILTERS and subrepos > 1:
            *_, url_path = repo.split("/")
            pyrepos[repo] = url_path
        elif language in PRECOMMIT_FILTERS and subrepos == 1:
            pyrepos[repo] = data[repo][0]["id"]

    logger.debug("Number of pre-commit hooks found: %s", len(pyrepos))
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
        r = requests.get(dst_url, headers=headers, timeout=15)
        data = r.json()
        version = data.get("name", 0)
        if not version:
            logger.debug("0 - for %s", url_src)
            return 0
        else:
            logger.debug("%s - for %s", version, url_src)
            return version
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from None


def get_latest_pypi_repo_version(name: str) -> Union[str, int]:
    """Given a repository name , find the latest version utilizing PyPI API.

    Parameters
    ----------
    name : str
        Supplied project name. This is not the URL.

    Returns
    -------
    version : str
        The latest repository version.

    0 :
        Indicates the repository was not found.

    Raises
    ------
    SystemExit:
        if requests.get() operations fails for any reason.
    """
    logger.debug("starting **** get_precommit_repos ****")
    int_url = "https://pypi.org/pypi/<project>/json"
    dst_url = int_url.replace("<project>", name)
    headers = {"Accept": "application/json"}
    try:
        r = requests.get(dst_url, headers=headers, timeout=15)
        data = r.json()
        if data.get("message", 0) == "Not Found":
            logger.debug("0 - for %s", name)
            return 0
        else:
            version = data["info"]["version"]
            logger.debug("%s - for %s", version, name)
            return version
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from None


def generate_db(force: int = 0) -> dict[str, str]:
    """Generate a mapping from pre-commit repo to PyPI repo.

    Generates a dictionary data structure:
    key : pre-commit URL
    value : PyPi project name
    e.g. {"https://github.com/pre-commit/pre-commit-hooks": "pre-commit-hooks",}

    Parameters
    ----------
    force : int
        When set to 1 will force the generation of a new mapping

    Returns
    -------
    mapping : dict
        the mapping dictionary
    """
    logger.debug("starting **** generate_db ****")

    def generate_file() -> dict:
        """Create the mapping dictionary is it does not exist or is out of date."""
        mapping_db = {}
        pyrepos = get_precommit_repos()
        logger.debug("List of precommit repositories: %s", pyrepos)
        for repo in tqdm(pyrepos):
            inta_repo, *_ = repo
            inta_repo = inta_repo.lower()
            mapping_db[inta_repo] = ""
            if inta_repo in MANUAL_MAPPING:
                logger.debug("adding value from manual mapping dict")
                mapping_db[inta_repo] = MANUAL_MAPPING[inta_repo]
            else:
                *_, project = inta_repo.split("/")
                result = get_latest_pypi_repo_version(project)
                if result != 0:
                    logger.debug("project found on PyPI...mapping value to key")
                    mapping_db[inta_repo] = project
        with MAPPING_FILE.open("w") as outfile:
            json.dump(mapping_db, outfile)
        return mapping_db

    with as_file(MAPPING_FILE) as mapping_file:
        if not mapping_file.exists() or force == 1 or mapping_file.stat().st_size < 5:
            logger.debug("Generating new mapping")
            mapping = generate_file()
        elif int(time.time() - os.path.getmtime(mapping_file)) > REGEN_PERIOD:
            logger.debug("mapping expired... Generating a new mapping")
            mapping = generate_file()
        else:
            logger.debug("Reusing mapping")
            mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    return mapping


def find_yaml_config_file() -> Path:
    """Find the '.pre-commit-config.yaml' config file in the project directory.

    Returns
    -------
    pc_file : Path
        Path object for the configuration file.

    Raises
    ------
    FileNotFoundError :
        If the config file cannot be found.
    """
    logger.debug("starting **** find_yaml_config_file ****")
    file_list_text = list(ROOT_DIR.iterdir())
    file_list_path = [Path(i) for i in file_list_text]
    for filepath in file_list_path:
        if filepath.name == PRECOMMIT_CONFIG_FILE:
            pc_file = filepath
            logger.debug("found file: %s", pc_file)
            return pc_file
    raise FileNotFoundError(f"Cannot locate '{PRECOMMIT_CONFIG_FILE}'")


def yaml_to_dict(yaml_file: Path) -> dict:
    """Get a list of repositories from the pre-commit config file.

    yaml data structure in python is {"repos": [ { }, { }, { } ] }
    so to get an individual repo & rev:
    1st repo - data["repos"][0]["repo"]
    1st rev - data["repos"][0]["rev"]

    Parameters
    ----------
    yaml_file : Path
        Pathlib.Path object to configuration file.

    Returns
    -------
    repos : dict
        Dictionary object mapping repository name to version.
    """
    logger.debug("starting **** yaml_to_dict ****")
    with open(yaml_file) as f:
        yaml_contents = yaml.safe_load(f)
    repos = {}
    for _, repo in enumerate(yaml_contents["repos"]):
        if repo["repo"] in ("local", "meta"):
            continue
        version = repo["rev"]
        version = _utility_remove_vee(version)
        repos[repo["repo"].strip().lower()] = version.strip()
    logger.debug("%s", repos)
    return repos


def update_yaml(yaml_file: Path, repo: str, version: str) -> None:
    """Update a repo in the '.pre-commit-config.yaml' file with the given version.

    Parameters
    ----------
    yaml_file : Path
        pathlib.Path object to the pre-commit config file.
    repo : str
        The URL string of the Repository to update.
    version : str
        String representation of the version to apply.
    """
    logger.debug("starting **** update_yaml ****")
    found_index = -1
    version = _utility_remove_vee(version)
    repo_list = yaml_to_dict(yaml_file)
    for index, file_repo in enumerate(repo_list):
        if repo in file_repo:
            found_index = index
            break
    if found_index == -1:
        raise NameError(f"Repository {repo} not found in 'pre-commit-config' file")
    with open(yaml_file) as f:
        yaml_contents = yaml.safe_load(f)
        yaml_contents["repos"][found_index]["rev"] = version
    with open(yaml_file, mode="w", encoding="utf-8") as file:
        yaml.dump(yaml_contents, file, sort_keys=False, indent=4)
        logger.debug("%s updated to version %s", repo, version)


def find_requirements_file() -> Any:
    """Find the first piptools generated file in the pip requirements tree.

    Given the root requirements file find and verify the final layered
    requirements file is a pip-tools generated file.

    Returns
    -------
    result : Path
        The pathlib.Path object to the derived requirement file.
    """
    logger.debug("starting **** find_requirements_file function ****")
    logger.debug("root requirement: %s", ROOT_REQUIREMENT)

    def next_file(req_file: Path) -> Any:
        with open(req_file) as f:
            lines = f.read()
            if "autogenerated by pip-compile" in lines:
                return req_file, 1
        with open(req_file) as f:
            lines = f.readlines()  # type:ignore
            for line in lines:
                if "-r " in line:
                    _, next_req = line.split(" ")
                    next_req = next_req.strip()
                    next_req = _utility_find_file_path(next_req)  # type:ignore
                    if next_req == 0:
                        raise FileNotFoundError("No Files found")
                    if next_req == 1:
                        logger.debug("found %s", next_req)
                        raise NameError("Ambiguous result - more than one file found")
                    return next_req, 0
                else:
                    raise FileNotFoundError(
                        "Requirement file generated by piptools " "Not found..."
                    )

    final = 0
    result = ROOT_REQUIREMENT
    while final == 0:
        result, final = next_file(result)
    if final == 1:
        filename = "".join([result.stem, result.suffix])
        logger.debug("Found requirement file: %s", filename)
        return result


def get_installed_version(package: str) -> Union[str, None]:
    """Return installed package version given the package name.

    This is the package version installed by pip and not the version in the
    requirements file or the pre-commit-config.yaml file

    Parameters
    ----------
    package : str
        The name of the installed package.

    Returns
    -------
    installed_version : str
        version of the package installed by pip.

    None :
        if the package is not found
    """
    logger.debug("starting **** get_installed_version function ****")
    try:
        installed_version = ver(package)
        logger.debug("package version found: %s", installed_version)
        return installed_version
    except PackageNotFoundError:
        logger.info("package not found")
        return None


def get_requirement_versions(req_file: Path, req_list: list) -> dict:
    """Get the repo version from the requirements file.

    Parameters
    ----------
    req_file : Path
        pathlib.Path object for the derived requirements file.
    req_list : list
        A list comprising packages that need versions.

    Returns
    -------
    req_version_list : dict
        A Dictionary comprising key: package name, Value: the version
        e.g. {'click': '8.1.3'}
    """
    logger.debug("starting **** get_requirement_versions function ****")
    req_version_list = {}
    with open(req_file) as f:
        lines = f.readlines()
        for line in lines:
            if "==" in line:
                package, version = line.split("==")
                version = _utility_remove_vee(version)
                if package in req_list:
                    req_version_list[package.strip()] = version.strip()
    return req_version_list


def main() -> int:
    load_settings()
    logger.debug(
        f"\nROOT_DIR: {'':20}{ROOT_DIR}\n" f"MAPPING_FILE: {'':20}{MAPPING_FILE}\n"
    )
    config_file = find_yaml_config_file()
    logger.debug("yaml config file: %s", config_file)
    yaml_dict = yaml_to_dict(config_file)
    logger.debug("yaml converted to dict: %s", yaml_dict)
    require_file = find_requirements_file()
    map_db = generate_db(force=0)
    pypi_repo_list = [map_db[repo] for repo in yaml_dict if map_db.get(repo, 0) != 0]
    logger.debug("PyPI repository list: %s", pypi_repo_list)
    req_versions = get_requirement_versions(require_file, pypi_repo_list)
    logger.debug("Requirement Version: %s", req_versions)

    mismatch = 0
    for repo in yaml_dict:
        if (precommit_ver := yaml_dict[repo]) != (
            piptools_ver := req_versions.get(pack := map_db.get(repo, ""), "-")
        ):
            if piptools_ver != "-":
                mismatch += 1
                logger.info(
                    f"{pack:15} - piptools: {piptools_ver:10} !=     "
                    f"pre-commit: {precommit_ver}"
                )
                if UPDATE_PC_YAML_FILE is True:
                    update_yaml(config_file, repo, piptools_ver)
    if mismatch > 0:
        return 1
    else:
        logger.info("Success! - pre-commit is in sync with piptools")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
