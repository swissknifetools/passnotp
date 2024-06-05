import pathlib

import pytest

from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.exceptions.profile import ProfileNotFound
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.query.get_profile.dto import GetProfileDTO
from libs.config.src.query.get_profile.handler import get_profile
from libs.config.src.util.config import write_config
from libs.config.tests.fixture.test_config_fixture import (
    config_multiple_profile_no_default,
    config_multiple_profile_with_default,
    config_no_profile,
    config_path_factory,
    config_single_profile_default,
    config_single_profile_no_default,
)
from libs.config.tests.fixture.test_profile_fixture import (
    profile_critical_false,
    profile_critical_true,
    profile_debug_false,
    profile_debug_true,
    profile_error_false,
    profile_error_true,
    profile_info_false,
    profile_info_true,
    profile_warning_false,
    profile_warning_true,
)


def test_profile_get(config_path_factory: pathlib.Path):
    config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    get_profile_dto = GetProfileDTO(fp=p, name="test")

    assert get_profile(get_profile_dto) == config.profiles["test"]


def test_profile_get_no_profile(config_path_factory: pathlib.Path):
    config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    get_profile_dto = GetProfileDTO(fp=p, name="project1")

    with pytest.raises(ProfileNotFound):
        get_profile(get_profile_dto)


def test_profile_get_no_valid_config(config_path_factory: pathlib.Path):
    config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    get_profile_dto = GetProfileDTO(fp=config_path_factory / "config.no_config", name="test")

    with pytest.raises(ConfigNotFound):
        get_profile(get_profile_dto)
