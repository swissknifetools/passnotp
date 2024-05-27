from pydantic import BaseModel, validator

from libs.shared.logging import LogLevel


class ProfileConfigModel(BaseModel):
    sqlite_url: str
    log_level: LogLevel = LogLevel.INFO
    exit: bool = False

class ProfileModel(BaseModel):
    name: str
    config: ProfileConfigModel
    
