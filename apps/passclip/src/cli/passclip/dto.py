import logging
from typing import Optional, TypedDict

from apps.passclip.src.app.core.settings import Settings
from libs.console_logger.src.constants import LogLevel


class CreatePassCliArgs(TypedDict):
    name: str
    secret: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class DeletePassCliArgs(TypedDict):
    name: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class UpdatePassCliArgs(TypedDict):
    name: str
    secret: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class GetPassCliArgs(TypedDict):
    name: str
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings


class ListPassCliArgs(TypedDict):
    prefix: Optional[str]
    log_level: LogLevel
    profile: Optional[str]
    settings: Settings
