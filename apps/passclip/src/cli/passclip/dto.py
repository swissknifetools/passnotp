import argparse
from typing import Optional, TypedDict

from apps.passclip.src.app.core.settings import Settings
from libs.console_logger.src.constants import LogLevel


class CreatePassCliArgs(argparse.Namespace):
    name: str
    secret: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class DeletePassCliArgs(argparse.Namespace):
    name: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class UpdatePassCliArgs(argparse.Namespace):
    name: str
    secret: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class GetPassCliArgs(argparse.Namespace):
    name: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class ListPassCliArgs(argparse.Namespace):
    prefix: Optional[str]
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings
