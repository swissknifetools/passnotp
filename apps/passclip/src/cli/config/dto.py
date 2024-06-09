from typing import TypedDict

from apps.passclip.src.app.core.settings import Settings


class InitConfigCliArgs(TypedDict):
    settings: Settings


class ShowConfigCliArgs(TypedDict):
    settings: Settings
