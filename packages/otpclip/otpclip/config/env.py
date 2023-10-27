import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.logging import LogLevel


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='PASSCLIP_', env_file=f".env.{os.environ.get('PASSCLIP_ENV', 'dev')}")
    
    LOGGING_LEVEL: LogLevel = LogLevel.DEBUG
    
environment = Settings()