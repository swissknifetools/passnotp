from libs.config.src.command.update_profile.dto import UpdateProfileDTO
from libs.config.src.exceptions.profile import ProfileNotFound
from libs.config.src.model.profile_model import ProfileConfigModel
from libs.config.src.util.config import read_config, write_config


def run(args: UpdateProfileDTO) -> ProfileConfigModel:
    """Command to update a profile in the config file.

    Args:
        fp (pathlib.Path): Config file path.
        args (UpdateProfileDTO): Update profile name and config.

    Raises:
        ProfileNotFound: Raised if the profile is not found in the config file.

    Returns:
        ProfileConfigModel: Updated profile.
    """
    config = read_config(args.fp)

    if args.name not in config.profiles:
        raise ProfileNotFound(args.name)

    profile = config.profiles[args.name]
    profile.sqlite_url = args.sqlite_url if args.sqlite_url else profile.sqlite_url
    profile.exit = args.exit if args.exit else profile.exit

    config.profiles[args.name] = profile
    write_config(args.fp, config)

    return config.profiles[args.name]
