import pathlib
from typing import List

from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.util.config import read_config


def list_profiles(fp: pathlib.Path) -> List[ProfileConfigModel]:
    """List all profiles in the config file.

    Args:
        fp (pathlib.Path): Config file path.

    Returns:
        List[ProfileConfigModel]: List of profiles.
    """
    config = read_config(fp)

    return config.profiles
