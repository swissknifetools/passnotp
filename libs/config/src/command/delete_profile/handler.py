from libs.config.src.command.delete_profile.dto import DeleteProfileDTO
from libs.config.src.exceptions.profile import ProfileNotFound
from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.util.config import read_config, write_config


def run(args: DeleteProfileDTO) -> ProfileConfigModel:
    """Delete a profile from the config file.

    Args:
        args (DeleteProfileDTO): Profile name.

    Raises:
        ProfileNotFound: Raised if the profile is not found in the config file.

    Returns:
        ProfileConfigModel: Deleted profile.

    """
    config = read_config(args.fp)

    if args.name not in config.profiles:
        raise ProfileNotFound(args.name)

    profile = config.profiles[args.name]

    del config.profiles[args.name]
    write_config(args.fp, config)

    return profile
