import logging

from apps.passclip.src.cli.passclip.dto import (
    CreatePassCliArgs,
    DeletePassCliArgs,
    GetPassCliArgs,
    ListPassCliArgs,
    UpdatePassCliArgs,
)

logger = logging.getLogger("passclip")


def create_pass(args: CreatePassCliArgs) -> None:
    logger.debug("pass: create_pass")
    logger.debug(args)


def delete_pass(args: DeletePassCliArgs) -> None:
    logger.debug("pass: delete_pass")
    logger.debug(args)


def update_pass(args: UpdatePassCliArgs) -> None:
    logger.debug("pass: update_pass")
    logger.debug(args)


def get_pass(args: GetPassCliArgs) -> None:
    logger.debug("pass: get_pass")
    logger.debug(args)


def list_pass(args: ListPassCliArgs) -> None:
    logger.debug("pass: list_pass")
    logger.debug(args)
