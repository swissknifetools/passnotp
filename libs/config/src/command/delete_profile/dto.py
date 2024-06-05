import pathlib

from pydantic import BaseModel


class DeleteProfileDTO(BaseModel):
    """Delete profile DTO.

    Args:
        fp (pathlib.Path): Path to the config file.
        name (str): Name of the profile to delete.
    """

    fp: pathlib.Path
    name: str
