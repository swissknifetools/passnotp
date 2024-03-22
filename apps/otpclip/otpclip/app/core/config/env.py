import os
from pathlib import Path

from pydantic import FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.logging import LogLevel


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='OTPCLIP_', env_file=f".env.{os.environ.get('OTPCLIP_ENV', 'local')}")
    
    LOGGING_LEVEL: LogLevel = LogLevel.DEBUG
    SQL_ALCHEMY_URL: 
    
environment = Settings()