"""Top-level package for piptools_sync."""
# Core Library modules
import configparser
import json
import logging.config
from importlib import resources

# Third party modules
import toml  # type: ignore
import yaml  # type: ignore

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

_yaml_text = resources.read_text("piptools_sync", "config.yaml")
yaml_config = yaml.safe_load(_yaml_text)

_json_text = resources.read_text("piptools_sync", "config.json")
json_config = json.loads(_json_text)

_ini_text = resources.read_text("piptools_sync", "config.ini")
_ini = configparser.ConfigParser()
_ini.optionxform = str  # type: ignore
_ini.read_string(_ini_text)
ini_config = {section: dict(_ini.items(section)) for section in _ini.sections()}

_toml_text = resources.read_text("piptools_sync", "config.toml")
toml_config = toml.loads(_toml_text)


__title__ = "piptools-sync"
__version__ = "0.1.0"
__author__ = "Stephen R A King"
__description__ = "A piptools pre-commit version sync utility"
__email__ = "stephen.ra.king@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Stephen R A King"
