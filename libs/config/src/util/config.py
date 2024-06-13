import pathlib

import toml

from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.model.profile_model import ProfileConfigModel


def exists_config(fp: pathlib.Path) -> bool:
    return fp.exists()


def read_config(fp: pathlib.Path) -> ConfigModel:
    """Utility function to read a config file given it's path.

    Args:
        fp (pathlib.Path): Config file path.

    Raises:
        ConfigNotFound: Raised if the config file is not found in the given path.

    Returns:
        ConfigModel: Config model with the profiles.
    """
    if not fp.exists():
        raise ConfigNotFound(fp)

    raw_config = toml.load(fp)
    profiles = {k: ProfileConfigModel(**v) for k, v in raw_config.items()}
    return ConfigModel(profiles=profiles)


def write_config(fp: pathlib.Path, config: ConfigModel) -> None:
    """Utility function to write a config file given it's path and config model.

    Args:
        fp (pathlib.Path): Config file path.
        config (ConfigModel): New configuration to write to the file.
    """
    with open(fp, "w") as f:
        toml.dump(config.model_dump()["profiles"], f)
