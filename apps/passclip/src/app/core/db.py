from sqlalchemy import create_engine

from libs.config.src.model.profile_model import ProfileConfigModel
from libs.console_logger.src.constants import LogLevel


def get_engine(profile: ProfileConfigModel, log_level: LogLevel):
    engine = create_engine(
        profile.sqlite_url,
        echo=True if log_level == LogLevel.DEBUG else False,
    )
    return engine
