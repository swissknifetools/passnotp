
from pathlib import Path
from typing import Optional

import toml
from config.model.config import ConfigModel


def get_config(fp: Path) -> Optional[ConfigModel]:
    if not fp.exists():
        return
    
    configuration = toml.load(fp)
    return ConfigModel(profiles=configuration)