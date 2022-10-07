"""Top-level package for piptools_sync."""
# Core Library modules
import logging.config
from importlib.resources import as_file, files
from pathlib import Path

# Third party modules
import git
import toml  # type: ignore
import yaml  # type: ignore

__title__ = "piptools-sync"
__version__ = "0.3.0"
__author__ = "Stephen R A King"
__description__ = "A piptools pre-commit version sync utility"
__email__ = "stephen.ra.king@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Stephen R A King"


ROOT_DIR = Path(git.Repo(".", search_parent_directories=True).working_tree_dir)

LOGGING_CONFIG = """
version: 1
disable_existing_loggers: False
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    stream: ext://sys.stdout
    formatter: basic
  file:
    class: logging.FileHandler
    level: DEBUG
    filename: piptools_sync.log
    encoding: utf-8
    formatter: timestamp

formatters:
  basic:
    style: "{"
    format: "{message:s}"
  timestamp:
    style: "{"
    format: "{asctime} - {levelname} - {name} - {message}"

loggers:
  init:
    handlers: [console, file]
    level: DEBUG
    propagate: False
"""

logging.config.dictConfig(yaml.safe_load(LOGGING_CONFIG))
logger = logging.getLogger("init")


source_json = files("piptools_sync").joinpath("mapping.json")
if not source_json.is_file():
    with as_file(source_json) as _json_file:
        _json_file.write_text("{}")
MAPPING_FILE = source_json


source = files("piptools_sync").joinpath("config.toml")
with as_file(source) as _toml_path:
    _toml_text = _toml_path.read_text()
    toml_config = toml.loads(_toml_text)
