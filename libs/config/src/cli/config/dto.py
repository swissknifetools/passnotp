import argparse
import pathlib
from os import path
from typing import Optional, TypedDict

from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    CONFIG_PATH: pathlib.Path = pathlib.Path(path.expanduser("~/.passnotp/config"))


class InitConfigCliArgs(argparse.Namespace):
    settings: ConfigSettings
    profile: Optional[str]
    sqlite_url: Optional[str]
    exit: Optional[bool]


class ShowConfigCliArgs(argparse.Namespace):
    settings: ConfigSettings
