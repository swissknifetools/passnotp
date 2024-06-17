import pathlib
from typing import Dict

from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.util.config import read_config


def run(fp: pathlib.Path) -> Dict[str, ProfileConfigModel]:
    """List all profiles in the config file.

    Args:
        fp (pathlib.Path): Config file path.

    Returns:
        Dict[str, ProfileConfigModel]: List of profiles.
    """
    config = read_config(fp)

    return config.profiles
