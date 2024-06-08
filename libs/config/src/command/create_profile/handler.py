from libs.config.src.command.create_profile.dto import CreateProfileDTO
from libs.config.src.exceptions.profile import ProfileAlreadyExists
from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.util.config import read_config, write_config


def create_profile(args: CreateProfileDTO) -> ProfileConfigModel:
    """Creates a new profile in the config file.

    Args:
        args (CreateProfileDTO): Profile name and config.

    Raises:
        ProfileAlreadyExists: Raised if the profile already exists in the config file.

    Returns:
        ProfileConfigModel: Created profile..
    """
    config = read_config(args.fp)

    if args.name in config.profiles:
        raise ProfileAlreadyExists(args.name)

    config.profiles[args.name] = ProfileConfigModel(
        sqlite_url=args.sqlite_url,
        exit=args.exit,
    )

    write_config(args.fp, config)

    return config.profiles[args.name]
