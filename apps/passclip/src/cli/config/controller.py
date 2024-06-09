import logging
import sys

from colors import color

from apps.passclip.src.cli.config.dto import InitConfigCliArgs, ShowConfigCliArgs
from libs.config.src.command.create_profile.dto import CreateProfileDTO
from libs.config.src.command.create_profile.handler import create_profile
from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.model.config_model import ConfigModel
from libs.config.src.util.config import read_config

logger = logging.getLogger("passclip")


def config_init(args: InitConfigCliArgs) -> ConfigModel:
    logger.debug("config: init")
    logger.debug(args)

    try:
        config_path = args.settings.CONFIG_PATH
        read_config(config_path)

        logger.warning(
            f"Config file {color(config_path, 'cyan')} already exists. Do you want to overwrite it? (y/n)"
        )
        answer = input()
        if answer.lower() != "y":
            sys.exit(0)
    except ConfigNotFound:
        profile = color("default", "orange")
        logger.info(f"Config file not found. Starting creation with {profile} profile.")

    logger.info("Please input SQLite connection url in sqlalchemy supported format: ")
    sqlite_url = input()

    logger.info("Please input preferred behaviour for exiting the program (true/false): ")
    exit_behaviour = input()

    create_profile(
        CreateProfileDTO(
            fp=args.settings.CONFIG_PATH,
            name="default",
            sqlite_url=sqlite_url,
            exit=exit_behaviour.lower() == "true",
            overwrite=True,
        )
    )

    logger.info("Created config file at " + color(args.settings.CONFIG_PATH, "cyan"))

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
