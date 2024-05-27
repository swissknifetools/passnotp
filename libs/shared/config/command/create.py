import toml
from pathlib import Path

from config.model.config import ConfigModel


def create_config(fp: Path, config: ConfigModel)-> None:
    fp.write_text(toml.dumps(config.profiles))