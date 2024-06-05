import pytest
import toml

from libs.config.src.model.config_model import ConfigModel
from libs.config.src.model.profile_model import ProfileConfigModel
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


@pytest.fixture(scope="session")
def config_no_profile() -> ConfigModel:
    return ConfigModel(profiles={})


@pytest.fixture(scope="session")
def config_single_profile_default(profile_debug_false: ProfileConfigModel) -> ConfigModel:
    return ConfigModel(profiles={"default": profile_debug_false})


@pytest.fixture(scope="session")
def config_single_profile_no_default(
    profile_debug_true: ProfileConfigModel, profile_info_false: ProfileConfigModel
) -> ConfigModel:
    return ConfigModel(
        profiles={
            "project1": profile_debug_true,
            "project2": profile_info_false,
        }
    )


@pytest.fixture(scope="session")
def config_multiple_profile_with_default(
    profile_debug_false: ProfileConfigModel,
    profile_debug_true: ProfileConfigModel,
    profile_info_false: ProfileConfigModel,
) -> ConfigModel:
    return ConfigModel(
        profiles={
            "default": profile_debug_false,
            "project1": profile_debug_true,
            "project2": profile_info_false,
        }
    )


@pytest.fixture(scope="session")
def config_multiple_profile_no_default(
    profile_debug_true: ProfileConfigModel, profile_info_false: ProfileConfigModel
) -> ConfigModel:
    return ConfigModel(
        profiles={
            "project1": profile_debug_true,
            "project2": profile_info_false,
        }
    )


@pytest.fixture(scope="session")
def config_path_factory(
    tmp_path_factory,
    config_no_profile,
    config_single_profile_default,
    config_single_profile_no_default,
    config_multiple_profile_with_default,
    config_multiple_profile_no_default,
) -> pytest.TempdirFactory:
    tmp_directory = tmp_path_factory.mktemp(".directory")
    p = tmp_directory / "config.no_profile"
    p.write_text(toml.dumps(config_no_profile.profiles))
    p = tmp_directory / "config.single_profile_default"
    p.write_text(toml.dumps(config_single_profile_default.profiles))
    p = tmp_directory / "config.single_profile_no_default"
    p.write_text(toml.dumps(config_single_profile_no_default.profiles))
    p = tmp_directory / "config.multiple_profile_with_default"
    p.write_text(toml.dumps(config_multiple_profile_with_default.profiles))
    p = tmp_directory / "config.multiple_profile_no_default"
    p.write_text(toml.dumps(config_multiple_profile_no_default.profiles))
    return tmp_directory
