from profile.model.profile import ProfileConfigModel, ProfileModel
from typing import Dict

from pydantic import BaseModel


class ConfigModel(BaseModel):
    profiles: Dict[str, ProfileConfigModel]