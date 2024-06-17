import argparse

from rich_argparse import RichHelpFormatter

from apps.passclip.src.cli.passclip.controller import (
    create_pass,
    delete_pass,
    get_pass,
    list_pass,
    update_pass,
)
from libs.config.src.cli.common import get_profile_arguments


def add_passclip_cli(
    command_sp: argparse._SubParsersAction,
    common_parser: argparse.ArgumentParser,
    no_color: bool = False,
) -> None:
    profile_parser = get_profile_arguments()

    # COMMANDS
    create_parser = command_sp.add_parser(
        "create",
        description="Create a new password entry.",
        parents=[common_parser, profile_parser],
        help="Create a new password entry.",
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    create_parser.add_argument("name", type=str, help="Name of the entry.")
    create_parser.add_argument("secret", type=str, help="Secret of the entry.")
    create_parser.set_defaults(func=create_pass)

    delete_parser = command_sp.add_parser(
        "delete",
        parents=[common_parser, profile_parser],
        help="Delete a password entry.",
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    delete_parser.add_argument("name", type=str, help="Name of the entry.")
    delete_parser.set_defaults(func=delete_pass)

    update_parser = command_sp.add_parser(
        "update",
        parents=[common_parser, profile_parser],
        help="Get a password entry.",
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    update_parser.add_argument("name", type=str, help="Name of the entry.")
    update_parser.add_argument(
        "secret",
        type=str,
        help="Secret of the entry",
    )
    update_parser.set_defaults(func=update_pass)

    get_parser = command_sp.add_parser(
        "get",
        parents=[common_parser, profile_parser],
        help="Get a password entry.",
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    get_parser.add_argument("name", type=str, help="Name of the entry.")
    get_parser.set_defaults(func=get_pass)

    list_parser = command_sp.add_parser(
        "list",
        parents=[common_parser, profile_parser],
        help="List all password entries.",
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    list_parser.add_argument("-pre", "--prefix", type=str, help="Prefix of the entries.")
    list_parser.set_defaults(func=list_pass)
