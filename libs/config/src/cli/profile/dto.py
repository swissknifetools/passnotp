import argparse
from typing import Optional

from libs.config.src.cli.config.dto import ConfigSettings


class ProfileCreateCliArgs(argparse.Namespace):
    settings: ConfigSettings
    name: str
    sqlite_url: Optional[str]
    exit: Optional[bool]


class ProfileUpdateCliArgs(argparse.Namespace):
    settings: ConfigSettings
    name: str
    sqlite_url: Optional[str]
    exit: Optional[bool]


class ProfileDeleteCliArgs(argparse.Namespace):
    settings: ConfigSettings
    name: str


class ProfileGetCliArgs(argparse.Namespace):
    settings: ConfigSettings
    name: str


class ProfileListCliArgs(argparse.Namespace):
    settings: ConfigSettings
    search: Optional[str]
