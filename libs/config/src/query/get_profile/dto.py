import pathlib

from pydantic import BaseModel


class GetProfileDTO(BaseModel):
    """Get profile DTO.

    Args:
        fp (pathlib.Path): Path to the config file.
        name (str): Name of the profile to get.

    """
    fp: pathlib.Path
    name: str
