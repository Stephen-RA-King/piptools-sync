"""Top-level package for piptools_sync."""
# Core Library modules
import logging.config
from importlib import resources

# Third party modules
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


__title__ = "piptools-sync"
__version__ = "0.1.0"
__author__ = "Stephen R A King"
__description__ = "A piptools pre-commit sync tool"
__email__ = "stephen.ra.king@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Stephen R A King"
