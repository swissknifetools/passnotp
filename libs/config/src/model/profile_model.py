from pydantic import BaseModel

from libs.console_logger.src.constants import LogLevel


class ProfileConfigModel(BaseModel):
    sqlite_url: str
    exit: bool = False

    class Config:
        use_enum_values = True
