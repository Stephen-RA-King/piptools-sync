# Core Library modules
from pathlib import Path

# Third party modules
import yaml  # type: ignore

ROOT_DIR = Path.cwd().parent.parent
config_file = ".pre-commit-config.yaml"


def find_yaml_config_file():
    pc_file = Path
    file_list_text = list(ROOT_DIR.iterdir())
    file_list_path = [Path(i) for i in file_list_text]
    for filepath in file_list_path:
        if filepath.name == config_file:
            pc_file = filepath
            break
    if pc_file:
        print(pc_file)
        return pc_file
    else:
        print(f"Configuration file '{config_file}' cannot be found")


def yaml_to_list(yaml_file) -> list:
    """Get a list of repositories from the config file"""
    """
    yaml data structure in python is {"repos": [ { }. { }, { } ]}
    so to get an individual repo & rev:
    1st repo - data["repos"][0]["repo"]
    1st rev - data["repos"][0]["rev"]
    """
    with open(yaml_file) as f:
        yaml_contents = yaml.safe_load(f)
    repos = []
    for index, repo in enumerate(yaml_contents["repos"]):
        extracted = [index, repo["repo"], repo["rev"]]
        repos.append(extracted)
    print(repos)
    return repos


def list_to_yaml(list_update):
    pass


def find_requirements_file():
    pass


def get_requirements(req_file):
    pass


def compare_versions():
    pass


yml_file = find_yaml_config_file()
yaml_to_list(yml_file)
