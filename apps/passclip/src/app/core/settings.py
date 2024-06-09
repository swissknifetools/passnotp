import logging
import pathlib
from logging import Logger
from os import path

from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("passclip")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PASSCLIP_")

    CONFIG_PATH: pathlib.Path = pathlib.Path(path.expanduser("~/.passclip/config"))

    @field_validator("CONFIG_PATH")
    def validate_config_path(cls, v: pathlib.Path) -> pathlib.Path:
        parent_dir = v.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
        return v


try:
    settings = Settings()
except ValidationError as e:
    logger.error(e)
    exit(1)
