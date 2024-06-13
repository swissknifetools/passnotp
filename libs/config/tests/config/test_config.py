import pathlib

from libs.config.src.model.config_model import ConfigModel
from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.util.config import exists_config, read_config, write_config
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


def test_config_write_and_read(
    config_path_factory: pathlib.Path,
    profile_debug_false: ProfileConfigModel,
    profile_debug_true: ProfileConfigModel,
):
    config = ConfigModel(
        profiles={
            "default": profile_debug_false,
            "test": profile_debug_true,
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)
    read_back_config = read_config(p)

    assert read_back_config == config


def test_config_write_and_read_no_profile(
    config_path_factory: pathlib.Path, config_no_profile: ConfigModel
):
    write_config(config_path_factory / "config.write_config", config_no_profile)
    read_back_config = read_config(config_path_factory / "config.write_config")

    assert read_back_config == config_no_profile


def test_config_write_and_read_single_profile_default(
    config_path_factory: pathlib.Path, config_single_profile_default: ConfigModel
):
    write_config(config_path_factory / "config.write_config", config_single_profile_default)
    read_back_config = read_config(config_path_factory / "config.write_config")

    assert read_back_config == config_single_profile_default


def test_config_write_and_read_single_profile_no_default(
    config_path_factory: pathlib.Path, config_single_profile_no_default: ConfigModel
):
    write_config(config_path_factory / "config.write_config", config_single_profile_no_default)
    read_back_config = read_config(config_path_factory / "config.write_config")

    assert read_back_config == config_single_profile_no_default


def test_config_write_and_read_multiple_profile_with_default(
    config_path_factory: pathlib.Path, config_multiple_profile_with_default: ConfigModel
):
    write_config(config_path_factory / "config.write_config", config_multiple_profile_with_default)
    read_back_config = read_config(config_path_factory / "config.write_config")

    assert read_back_config == config_multiple_profile_with_default


def test_config_write_and_read_multiple_profile_no_default(
    config_path_factory: pathlib.Path, config_multiple_profile_no_default: ConfigModel
):
    write_config(config_path_factory / "config.write_config", config_multiple_profile_no_default)
    read_back_config = read_config(config_path_factory / "config.write_config")

    assert read_back_config == config_multiple_profile_no_default


def test_config_exists(
    config_path_factory: pathlib.Path,
    profile_debug_false: ProfileConfigModel,
    profile_debug_true: ProfileConfigModel,
):
    assert exists_config(config_path_factory / "config.test_config_exists") is False
    write_config(
        config_path_factory / "config.test_config_exists",
        ConfigModel(
            profiles={
                "default": profile_debug_false,
                "test": profile_debug_true,
            }
        ),
    )
    assert exists_config(config_path_factory / "config.test_config_exists") is True
