"""Top-level package for piptools_sync."""
# Core Library modules
import logging.config
from importlib import resources
from pathlib import Path

# Third party modules
import git
import toml  # type: ignore
import yaml  # type: ignore

__title__ = "piptools-sync"
__version__ = "0.1.0"
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
    format: "{levelname:s}:{name:s}:{message:s}"
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

with resources.path("piptools_sync", "mapping.json") as path:
    MAPPING_FILE = path


_toml_text = resources.read_text("piptools_sync", "config.toml")
toml_config = toml.loads(_toml_text)
