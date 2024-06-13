from calendar import c

from libs.config.src.exceptions.profile import ProfileNotFound
from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.query.get_profile.dto import GetProfileDTO
from libs.config.src.util.config import read_config


def get_profile(args: GetProfileDTO) -> ProfileConfigModel:
    """Get a profile from the config file.

    Args:
        args (GetProfileDTO): Profile name.

    Raises:
        ProfileNotFound: Raised if the profile is not found in the config file.

    Returns:
        ProfileConfigModel: Profile config.
    """
    config = read_config(args.fp)

    if args.name not in config.profiles:
        raise ProfileNotFound(f"Profile {args.name} not found in config file {args.fp}!")

    return config.profiles[args.name]
