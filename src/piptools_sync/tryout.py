"""A pre-commit utility plugin to verify requirement versions determined by
pip-tools are utilized by pre-commit
"""

# Core Library modules
import json
import os
import time
from pathlib import Path

# Third party modules
import pkg_resources
import requests
import yaml
from tqdm import tqdm

ROOT_DIR = Path.cwd().parent.parent
SRC_DIR = Path.cwd()
MAPPING_FILE = SRC_DIR / "mapping.json"
PRECOMMIT_CONFIG_FILE = ".pre-commit-config.yaml"
PRECOMMIT_REPOS_URL = "https://pre-commit.com/all-hooks.json"

# TODO: store thr following in a settings.yaml file
ROOT_REQUIREMENT = ROOT_DIR / "requirements.txt"
REGEN_PERIOD = 604800  # one week
UPDATE_PC_YAML_FILE = True

MANUAL_MAPPING = {
    "https://github.com/pre-commit/mirrors-autopep8": "autopep8",
    "https://github.com/pre-commit/mirrors-mypy": "mypy",
    "https://github.com/pre-commit/mirrors-yapf": "yapf",
    "https://github.com/FalconSocial/pre-commit-mirrors-pep257": "pep257",
}


def _utility_find_file_path(partial_path: str):
    """Given a partial file path, find the absolute file path for the file searching
    only from the project root.
    """

    result_list = sorted(Path(ROOT_DIR).glob(partial_path))
    if len(result_list) != 1:
        return 0
    else:
        return result_list[0]


def _utility_remove_vee(version):
    vee, *rest = version
    if vee in ["v", "V"]:
        version = "".join(rest)
    return version


def get_precommit_repos():
    """Get a list of repos from pre-commit.com that are relevant to python.

    data structure: {'html repo name': [ { } { } ] }
    Not used in v0.1.0
    """
    # TODO: improve the performance of this process (asyncio ?)
    pyrepos = []
    filters = ["python", "toml"]

    r = requests.get(PRECOMMIT_REPOS_URL)
    data = r.json()
    for repo in data:
        sublist = [repo]
        for _, subrepo in enumerate(data[repo]):
            if subrepo["language"] in filters:
                sublist.append(subrepo["name"])
        if len(sublist) > 1:
            pyrepos.append(sublist)
    return pyrepos


def get_latest_github_repo_version(url_src):
    """Given a repo URL, this function will look up the latest version
    from GitHub.
    """

    url_int = url_src.replace("https://github.com/", "https://api.github.com/repos/")
    dst_url = "".join([url_int, "/releases/latest"])
    headers = {"Accept": "application/vnd.github+json"}
    try:
        r = requests.get(dst_url, headers=headers)
        data = r.json()
        version = data.get("name", 0)
        if not version:
            return 0
        else:
            return version
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from None


def get_latest_pypi_repo_version(name):
    """Given a repository name , this function will check if the repository
    exists on PyPI.
    """
    int_url = "https://pypi.org/pypi/<project>/json"
    dst_url = int_url.replace("<project>", name)
    headers = {"Accept": "application/json"}
    try:
        r = requests.get(dst_url, headers=headers)
        data = r.json()
        if data.get("message", 0) == "Not Found":
            return 0
        else:
            version = data["info"]["version"]
            return version
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from None


def generate_db(force=0):
    """Generate a mapping from pre-commit repo to PyPI repo"""

    def generate_file():
        mapping_db = {}
        pyrepos = get_precommit_repos()
        for repo in tqdm(pyrepos):
            inta_repo, *_ = repo
            inta_repo = inta_repo.lower()
            mapping_db[inta_repo] = ""
            if inta_repo in MANUAL_MAPPING:
                mapping_db[inta_repo] = MANUAL_MAPPING[inta_repo]
            else:
                *_, project = inta_repo.split("/")
                result = get_latest_pypi_repo_version(project)
                if result != 0:
                    mapping_db[inta_repo] = project
        with open("mapping.json", "w") as outfile:
            json.dump(mapping_db, outfile)
        return mapping_db

    start = time.time()
    if not MAPPING_FILE.exists() or force == 1:
        print("Generating new mapping")
        mapping = generate_file()
    elif int(time.time() - os.path.getmtime(MAPPING_FILE)) > REGEN_PERIOD:
        print("mapping expired... Generating a new mapping")
        mapping = generate_file()
    else:
        print("Reusing mapping")
        with open("mapping.json") as infile:
            mapping = json.load(infile)
    end = time.time()
    print(end - start)

    return mapping


def find_yaml_config_file():
    """Find the '.pre-commit-config.yaml' config file in the project directory
    structure.
    """

    pc_file = Path
    file_list_text = list(ROOT_DIR.iterdir())
    file_list_path = [Path(i) for i in file_list_text]
    for filepath in file_list_path:
        if filepath.name == PRECOMMIT_CONFIG_FILE:
            pc_file = filepath
            break
    if pc_file:
        return pc_file
    else:
        print(f"Configuration file '{PRECOMMIT_CONFIG_FILE}' cannot be found")


def yaml_to_dict(yaml_file) -> dict:
    """Get a list of repositories from the config file

    yaml data structure in python is {"repos": [ { }. { }, { } ]}
    so to get an individual repo & rev:
    1st repo - data["repos"][0]["repo"]
    1st rev - data["repos"][0]["rev"]
    """

    with open(yaml_file) as f:
        yaml_contents = yaml.safe_load(f)
    repos = {}
    for _, repo in enumerate(yaml_contents["repos"]):
        version = repo["rev"]
        version = _utility_remove_vee(version)
        repos[repo["repo"].strip().lower()] = version.strip()
    return repos


def update_yaml(yaml_file, repo: str, version: str) -> None:
    """update a given repo in the '.pre-commit-config.yaml' config file with the
    given version.
    """

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
    with open(yaml_file, mode="wt", encoding="utf-8") as file:
        yaml.dump(yaml_contents, file)


def find_requirements_file():
    """Find the first piptools generated file in the pip requirements tree.

    Given the root requirements file find and verify the final layered
    requirements file is a pip-tools generated file
    """

    def next_file(req_file):
        with open(req_file) as f:
            lines = f.read()
            if "autogenerated by pip-compile" in lines:
                return req_file, 1
        with open(req_file) as f:
            lines = f.readlines()
            for line in lines:
                if "-r " in line:
                    _, next_req = line.split(" ")
                    next_req = next_req.strip()
                    next_req = _utility_find_file_path(next_req)
                    if next_req == 0:
                        raise NameError("Ambiguous result - more than one file found")
                    return next_req, 0
                else:
                    return "", -1

    final = 0
    result = ROOT_REQUIREMENT
    while final == 0:
        result, final = next_file(result)
    if final == 1:
        return result
    elif final == -1:
        print("piptools generated requirement Not found...")


def get_installed_version(package):
    installed_version = ""
    try:
        installed_version = pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        print("Not found")
    if installed_version:
        print(installed_version)
        return installed_version
    else:
        return None


def get_requirement_versions(req_file, req_list):
    """Get the repo version from the requirements file"""
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


if __name__ == "__main__":
    config_file = find_yaml_config_file()
    yaml_dict = yaml_to_dict(config_file)
    require_file = find_requirements_file()
    map_db = generate_db(force=0)
    pypi_repo_list = [map_db[repo] for repo in yaml_dict if map_db.get(repo, 0) != 0]
    req_versions = get_requirement_versions(require_file, pypi_repo_list)

    mismatch = 0
    for repo in yaml_dict:
        if (precommit_ver := yaml_dict[repo]) != (
            piptools_ver := req_versions.get(pack := map_db.get(repo, ""), "-")
        ):
            if piptools_ver != "-":
                mismatch += 1
                print(
                    f"{pack:15} - piptools: {piptools_ver:10} !=     "
                    f"pre-commit: {precommit_ver}"
                )
    if mismatch > 0:
        SystemExit(-1)
    else:
        SystemExit(0)
