from pydantic import BaseModel

from libs.console_logger.src.constants import LogLevel


class ProfileConfigModel(BaseModel):
    sqlite_url: str
    log_level: LogLevel = LogLevel.INFO
    exit: bool = False

    class Config:
        use_enum_values = True
