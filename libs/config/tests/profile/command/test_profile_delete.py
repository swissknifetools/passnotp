import pathlib

import pytest

from libs.config.src.command.delete_profile.dto import DeleteProfileDTO
from libs.config.src.command.delete_profile.handler import delete_profile
from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.exceptions.profile import ProfileNotFound
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.util.config import read_config, write_config
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


def test_delete_profile(config_path_factory: pathlib.Path):
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
            "project1": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    delete_profile_dto = DeleteProfileDTO(
        fp=p,
        name="project1",
    )
    returned_profile = delete_profile(delete_profile_dto)

    read_back_config = read_config(p)
    assert read_back_config == ConfigModel(
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
    assert returned_profile == config.profiles["project1"]


def test_delete_profile_no_valid_config(config_path_factory: pathlib.Path):
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
            "project1": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    delete_profile_dto = DeleteProfileDTO(
        fp=config_path_factory / "config.no_config",
        name="project1",
    )

    with pytest.raises(ConfigNotFound):
        delete_profile(delete_profile_dto)


def test_delete_profile_no_profile(config_path_factory: pathlib.Path):
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
            "project1": {
                "sqlite_url": "localhost:1433",
                "log_level": "DEBUG",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    delete_profile_dto = DeleteProfileDTO(
        fp=p,
        name="project2",
    )

    with pytest.raises(ProfileNotFound):
        delete_profile(delete_profile_dto)
