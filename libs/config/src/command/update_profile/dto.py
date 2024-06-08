import pathlib

from pydantic import BaseModel

from libs.console_logger.src.constants import LogLevel


class UpdateProfileDTO(BaseModel):
    """Update profile DTO.

    Args:
        fp (pathlib.Path): Path to the config file.
        name (str): Name of the profile to update.
        sqlite_url (str): SQLite URL for the profile.
        log_level (LogLevel, optional): Log level for the profile. Defaults to LogLevel.INFO.
        exit (bool, optional): Flag to indicate if the profile should exit the program. Defaults to False.
    """

    fp: pathlib.Path
    name: str
    sqlite_url: str
    exit: bool = False
