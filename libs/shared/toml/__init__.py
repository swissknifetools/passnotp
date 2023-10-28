from pathlib import Path
from typing import Optional

import toml


def get_version_from_toml(filepath: Path) -> Optional[str]:
    if not filepath.exists():
        return
    
    content = toml.load(filepath)
    return content.get("tool", {}).get("poetry", {}).get("version")
