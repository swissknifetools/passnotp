import pathlib

import pytest

from libs.config.src.cli.config.controller import config_show
from libs.config.src.cli.config.dto import ConfigSettings, ShowConfigCliArgs
from libs.config.src.model.config_model import ConfigModel
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


def test_config_show_existing_config(
    config_path_factory: pathlib.Path, profile_debug_false, profile_debug_true
):
    config = ConfigModel(
        profiles={
            "default": profile_debug_false,
            "test": profile_debug_true,
        }
    )

    p = config_path_factory / "config.write_config"
    write_config(p, config)

    config_show_dto = ShowConfigCliArgs(settings=ConfigSettings(CONFIG_PATH=p))
    try:
        config = config_show(config_show_dto)
    except Exception as e:
        pytest.fail(e)


def test_config_show_no_config(config_path_factory: pathlib.Path):
    pass
