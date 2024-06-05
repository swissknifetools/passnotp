from typing import Dict, Optional

from pydantic import BaseModel

from libs.config.src.model.profile_model import ProfileConfigModel


class ConfigModel(BaseModel):
    profiles: Optional[Dict[str, ProfileConfigModel]] = None
