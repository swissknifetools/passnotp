import argparse
from typing import List

from rich_argparse import RichHelpFormatter

from libs.config.src.cli.profile.controller import (
    profile_create,
    profile_delete,
    profile_get,
    profile_list,
    profile_update,
)


def add_profile_cli(
    command_sp: argparse._SubParsersAction,
    parents: List[argparse.ArgumentParser],
    no_color: bool = False,
) -> None:
    # PROFILE COMMANDS
    profile_parser = command_sp.add_parser(
        "profile",
        help="Profile utility commands.",
        parents=parents,
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    profile_parser.set_defaults(func=profile_parser.print_help)
    profile_subparsers = profile_parser.add_subparsers(title="profile", dest="subcommand")

    # PROFILE COMMANDS
    create_profile_parser = profile_subparsers.add_parser(
        "create",
        help="Create a new profile.",
        description="Create a new profile in passclip's config file.",
        parents=[*parents],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    create_profile_parser.add_argument("name", type=str, help="Name of the profile.")
    create_profile_parser.add_argument(
        "--sqlite_url", type=str, required=True, help="SQLite connection URL."
    )
    create_profile_parser.add_argument(
        "--exit",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Flag to indicate if the terminal should exit after commands are executed.",
    )
    create_profile_parser.set_defaults(func=profile_create)

    delete_profile_parser = profile_subparsers.add_parser(
        "delete",
        help="Delete a profile.",
        description="Delete a profile from passclip's config file.",
        parents=[*parents],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    delete_profile_parser.add_argument("name", type=str, help="Name of the profile.")
    delete_profile_parser.set_defaults(func=profile_delete)

    update_profile_parser = profile_subparsers.add_parser(
        "update",
        help="Update a profile.",
        description="Update a profile in passclip's config file.",
        parents=[*parents],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    update_profile_parser.add_argument("name", type=str, help="Name of the profile.")
    update_profile_parser.add_argument(
        "--sqlite_url", type=str, required=True, help="SQLite connection URL."
    )
    update_profile_parser.add_argument(
        "--exit",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Flag to indicate if the terminal should exit after commands are executed.",
    )
    update_profile_parser.set_defaults(func=profile_update)

    get_profile_parser = profile_subparsers.add_parser(
        "get",
        help="Get a profile.",
        description="Get a profile from passclip's config file.",
        parents=[*parents],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    get_profile_parser.add_argument("name", type=str, help="Name of the profile.")
    get_profile_parser.set_defaults(func=profile_get)

    list_profile_parser = profile_subparsers.add_parser(
        "list",
        help="List all profiles.",
        description="List all profiles in passclip's config file.",
        parents=[*parents],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    list_profile_parser.add_argument("-s", "--search", type=str, help="Search for a profile.")
    list_profile_parser.set_defaults(func=profile_list)
