import os
import pathlib
from os import path

import pytest

from apps.passclip.src.app.core.settings import Settings


def test_default_settings():
    settings = Settings()
    assert settings.CONFIG_PATH == pathlib.Path(path.expanduser("~/.passclip/config"))


def test_env_settings(tmp_path_factory: pytest.TempPathFactory):
    d = tmp_path_factory.mktemp(".passclip")
    p = d / "config"
    os.environ["PASSCLIP_CONFIG_PATH"] = p.absolute().as_posix()

    settings = Settings()
    assert settings.CONFIG_PATH == p


def test_config_path_creation(tmp_path_factory: pytest.TempPathFactory):
    d = tmp_path_factory.mktemp(".passclip")
    p = d / "directory" / "config"
    os.environ["PASSCLIP_CONFIG_PATH"] = p.absolute().as_posix()
    assert p.exists() is False

    settings = Settings()
    assert settings.CONFIG_PATH == p
    assert p.exists() is False
    assert p.is_dir() is False
    assert p.parent.exists() is True
    assert p.parent.is_dir() is True
