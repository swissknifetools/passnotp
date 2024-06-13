import logging
import sys

from colors import color

from libs.config.src.cli.config.dto import InitConfigCliArgs, ShowConfigCliArgs
from libs.config.src.command.create_profile.dto import CreateProfileDTO
from libs.config.src.command.create_profile.handler import create_profile
from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.query.get_profile.dto import GetProfileDTO
from libs.config.src.query.get_profile.handler import get_profile
from libs.config.src.util.config import exists_config, read_config

logger = logging.getLogger("passclip")


def config_init(args: InitConfigCliArgs) -> ConfigModel:
    logger.debug("config: init")
    logger.debug(args)

    config_path = args.settings.CONFIG_PATH
    profile_name = args.profile

    logger.info(
        color("Welcome to passclip!. Initializing config file at: ", "orange")
        + color(config_path, "cyan")
    )
    logger.info(color(f"Profile provided: {profile_name} ", "orange"))

    if exists_config(config_path):
        answer = input(
            f"Config file {color(config_path, 'cyan')} already exists. Do you want to overwrite it? (y/n): "
        )

        if answer.strip().lower() != "y":
            sys.exit(0)

    # DO NOT CHANGE THE MESSAGE STRING CONCATENATION, BLACK FORMATTING IS NOT WORKING
    if args.sqlite_url is None:
        message = color("sqlite_url", "orange") + color("(sqlite://passclip.db)", "green") + ": "
        sqlite_url = input(message).strip() or "sqlite://passclip.db"
        if not sqlite_url:
            logger.error("SQLite URL is required!")
            sys.exit(1)
    else:
        sqlite_url = args.sqlite_url

    if args.exit is None:
        message = color("exit", "orange") + color("(false)", "green") + ": "
        exit_behaviour = input(message).strip().lower() or "false"
        if exit_behaviour not in ["true", "false"]:
            logger.error("Exit flag must be true or false!")
            sys.exit(1)
    else:
        exit_behaviour = args.exit

    create_profile(
        CreateProfileDTO(
            fp=args.settings.CONFIG_PATH,
            name=profile_name,
            sqlite_url=sqlite_url,
            exit=exit_behaviour,
            overwrite=True,
        )
    )

    logger.info(
        color("Created config file at ", "orange")
        + color(args.settings.CONFIG_PATH, "cyan")
        + color(" successfully!", "green")
    )

    return read_config(config_path)


def config_show(args: ShowConfigCliArgs) -> None:
    logger.debug("config: show")
    logger.debug(args)

    try:
        config_path = args.settings.CONFIG_PATH
        config = read_config(config_path)
        logger.info(config)
    except ConfigNotFound:
        logger.info(
            f"Config file {color(config_path, 'cyan')} was not found. Do you want to create it? (y/n)"
        )
        answer = input()
        if answer.lower() == "n":
            sys.exit(0)
        else:
            config = config_init(args)
            logger.info(config)
