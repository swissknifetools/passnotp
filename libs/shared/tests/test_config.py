from pathlib import Path

import pytest
import toml
from tests.fixtures.profiles import single_profile_default

from libs.shared.config import read_config


@pytest.fixture(scope='session')
def single_profile_default_path (tmp_path_factory, single_profile_default):
    tmp_directory = tmp_path_factory.mktemp('.passnotp')
    p = tmp_directory / 'config.single_profile_default'
    p.write_text(toml.dumps(single_profile_default))
    return p
    
@pytest.fixture(scope='session')
def single_profile_no_default_path(tmp_path_factory, single_profile_no_default):
    tmp_directory = tmp_path_factory.mktemp('.passnotp')
    p = tmp_directory / 'config.single_profile_default'
    p.write_text(toml.dumps(single_profile_default))
    return p

def test_exists(single_profile_default_default_path, single_profile_default):
    assert read_config(Path('doesntexist')) == None
    assert read_config(single_profile_default_default_path) == single_profile_default
    