import logging
import sys

from colors import color

from libs.config.src.cli.profile.dto import (
    ProfileCreateCliArgs,
    ProfileDeleteCliArgs,
    ProfileGetCliArgs,
    ProfileListCliArgs,
    ProfileUpdateCliArgs,
)
from libs.config.src.command.create_profile.dto import CreateProfileDTO
from libs.config.src.command.create_profile.handler import run as create_profile_cmd
from libs.config.src.command.delete_profile.dto import DeleteProfileDTO
from libs.config.src.command.delete_profile.handler import run as delete_profile_cmd
from libs.config.src.command.update_profile.dto import UpdateProfileDTO
from libs.config.src.command.update_profile.handler import run as update_profile_cmd
from libs.config.src.exceptions.config import ConfigNotFound
from libs.config.src.exceptions.profile import ProfileAlreadyExists, ProfileNotFound
from libs.config.src.query.get_profile.dto import GetProfileDTO
from libs.config.src.query.get_profile.handler import run as get_profile_qry
from libs.config.src.query.list_profile.handler import run as list_profiles_qry

logger = logging.getLogger("passclip")


def profile_create(args: ProfileCreateCliArgs) -> None:
    logger.debug("profile: create")
    logger.debug(args)

    create_profile_dto = CreateProfileDTO(
        fp=args.settings.CONFIG_PATH,
        name=args.name,
        sqlite_url=args.sqlite_url,
        exit=args.exit or False,
    )

    try:
        create_profile_cmd(create_profile_dto)
    except ProfileAlreadyExists:
        message = f"Profile {color(args.name, 'orange')} already exists!"
        logger.warning(message)

        question = f"Would you like to overwrite it? {color('(y/n)', 'orange')}: "
        answer = input(question)
        if answer.strip().lower() != "y":
            sys.exit(0)

        create_profile_dto.overwrite = True

        create_profile_cmd(create_profile_dto)


def profile_delete(args: ProfileDeleteCliArgs) -> None:
    logger.debug("profile: delete")
    logger.debug(args)

    message = f"Profile {color(args.name, 'orange')} will be deleted! This action cannot be undone!"
    logger.warning(message)

    question = f"Are you sure you want to delete it? {color('(y/n)', 'orange')}: "
    answer = input(question)
    if answer.strip().lower() != "y":
        sys.exit(0)

    delete_profile_dto = DeleteProfileDTO(
        fp=args.settings.CONFIG_PATH,
        name=args.name,
    )
    delete_profile_cmd(delete_profile_dto)


def profile_update(args: ProfileUpdateCliArgs) -> None:
    logger.debug("profile: update")
    logger.debug(args)

    update_profile_dto = UpdateProfileDTO(
        name=args.name,
        sqlite_url=args.sqlite_url,
        exit=args.exit or False,
        fp=args.settings.CONFIG_PATH,
    )

    try:
        update_profile_cmd(update_profile_dto)
    except (ProfileNotFound, ConfigNotFound):
        question = f"Would you like to create it? {color('(y/n)', 'orange')}: "
        answer = input(question)
        if answer.strip().lower() != "y":
            sys.exit(0)

        create_profile_dto = CreateProfileDTO(
            fp=args.settings.CONFIG_PATH,
            name=args.name,
            sqlite_url=args.sqlite_url,
            exit=args.exit or False,
        )
        create_profile_cmd(create_profile_dto)


def profile_get(args: ProfileGetCliArgs) -> None:
    logger.debug("profile: get")
    logger.debug(args)

    get_profile_dto = GetProfileDTO(fp=args.settings.CONFIG_PATH, name=args.name)

    try:
        profile = get_profile_qry(get_profile_dto)
    except ProfileNotFound:
        logger.error("Profile not found!")
        sys.exit(1)

    logger.info(f"{color("Name:", "cyan")}              {args.name}")
    logger.info(f"{color("SQLite URL:", "cyan")}        {profile.sqlite_url}")
    logger.info(f"{color('Exit:', 'cyan')}              {profile.exit}")


def profile_list(args: ProfileListCliArgs) -> None:
    logger.debug("profile: list")
    logger.debug(args)

    try:
        profiles = list_profiles_qry(args.settings.CONFIG_PATH)
    except ConfigNotFound:
        logger.error("Config file not found!")
        sys.exit(1)

    logger.info(f"{color('Profiles:', 'orange')}")
    logger.info(f"{color('=' * 40, 'green')}")
    for name, profile in profiles.items():
        logger.info(f"{color("Name:", "cyan")}              {name}")
        logger.info(f"{color("SQLite URL:", "cyan")}        {profile.sqlite_url}")
        logger.info(f"{color('Exit:', 'cyan')}              {profile.exit}")
        logger.info(f"{color('-' * 40, 'blue')}")
