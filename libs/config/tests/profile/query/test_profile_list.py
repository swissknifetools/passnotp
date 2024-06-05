import pathlib

import pytest

from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.exceptions.profile import ProfileNotFound
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.query.list_profile.handler import list_profiles
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


def test_profile_list(config_path_factory: pathlib.Path):
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

    list_profiles_dto = list_profiles(p)

    assert list_profiles_dto == config.profiles


def test_profile_list_no_valid_config(config_path_factory: pathlib.Path):
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

    with pytest.raises(ConfigNotFound):
        list_profiles(config_path_factory / "config.no_config")
