import pytest
from pydantic import ValidationError

from libs.config.src.model.profile_model import ProfileConfigModel
from libs.console_logger.src.constants import LogLevel


def test_profile_config_model():
    profile = ProfileConfigModel(sqlite_url="localhost:1433", log_level=LogLevel.DEBUG, exit=False)

    assert profile.sqlite_url == "localhost:1433"
    assert profile.log_level == LogLevel.DEBUG
    assert profile.exit is False

    text_log_level = ProfileConfigModel(sqlite_url="localhost:1433", log_level="DEBUG", exit=False)
    assert text_log_level.sqlite_url == "localhost:1433"
    assert text_log_level.log_level == LogLevel.DEBUG
    assert text_log_level.exit is False

    with pytest.raises(ValidationError):
        ProfileConfigModel(sqlite_url="localhost:1433", log_level="WRONG", exit=False)
