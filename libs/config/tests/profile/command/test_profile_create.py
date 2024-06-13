import pathlib

import pytest

from libs.config.src.command.create_profile.dto import CreateProfileDTO
from libs.config.src.command.create_profile.handler import create_profile
from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.exceptions.profile import ProfileAlreadyExists
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.model.profile_model import ProfileConfigModel
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


def test_create_profile(config_path_factory: pathlib.Path):
    config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
        }
    )

    profile_dto = CreateProfileDTO(
        name="project1",
        sqlite_url="localhost:1433",
        exit=False,
        fp=config_path_factory / "config.write_config",
    )

    expected_config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "project1": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)
    create_profile(profile_dto)

    read_back_config = read_config(p)
    assert read_back_config == expected_config


def test_create_profile_already_exists(config_path_factory: pathlib.Path):
    config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "project1": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    profile_dto = CreateProfileDTO(
        name="project1",
        sqlite_url="localhost:1433",
        exit=False,
        fp=config_path_factory / "config.write_config",
    )

    with pytest.raises(ProfileAlreadyExists):
        create_profile(profile_dto)


def test_create_profile_already_exists_overwrite(config_path_factory: pathlib.Path):
    config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "project1": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    profile_dto = CreateProfileDTO(
        name="project1",
        sqlite_url="localhost:1434",
        exit=False,
        fp=config_path_factory / "config.write_config",
        overwrite=True,
    )

    expected_config = ConfigModel(
        profiles={
            "default": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "test": {
                "sqlite_url": "localhost:1433",
                "exit": False,
            },
            "project1": {
                "sqlite_url": "localhost:1434",
                "exit": False,
            },
        }
    )

    create_profile(profile_dto)

    read_back_config = read_config(p)
    assert read_back_config == expected_config


def test_create_profile_no_valid_config(config_path_factory: pathlib.Path):
    profile_dto = CreateProfileDTO(
        name="project1",
        sqlite_url="localhost:1433",
        exit=False,
        fp=config_path_factory / "config.test_create_profile_no_valid_config",
    )

    create_profile(profile_dto)

    read_back_config = read_config(
        config_path_factory / "config.test_create_profile_no_valid_config"
    )
    assert read_back_config == ConfigModel(
        profiles={"project1": ProfileConfigModel(sqlite_url="localhost:1433", exit=False)}
    )
