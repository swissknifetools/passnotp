import argparse
from typing import List

from rich_argparse import RichHelpFormatter

from libs.config.src.cli.config.controller import config_init, config_show


def add_config_cli(
    command_sp: argparse._SubParsersAction,
    parents: List[argparse.ArgumentParser],
    no_color: bool = False,
) -> None:
    profile_cli = get_profile_cli()

    config_parser: argparse.ArgumentParser = command_sp.add_parser(
        "config",
        help="Configuration commands",
        parents=parents,
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    config_parser.set_defaults(func=config_parser.print_help)
    config_subparsers = config_parser.add_subparsers(title="config", dest="subcommand")

    # COMMANDS
    init_config_parser = config_subparsers.add_parser(
        "init",
        help="Initialize a new config file.",
        description="Initialize passclip's config file.",
        parents=[profile_cli, *parents],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    init_config_parser.add_argument("--sqlite_url", type=str, help="SQLite connection URL.")
    init_config_parser.add_argument(
        "--exit",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Flag to indicate if the terminal should exit after commands are executed.",
    )
    init_config_parser.set_defaults(func=config_init)

    show_config_parser = config_subparsers.add_parser(
        "show",
        help="Show the config file.",
        parents=parents,
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    show_config_parser.set_defaults(func=config_show)


def get_profile_cli():
    profile_parser = argparse.ArgumentParser(add_help=False)
    profile_parser.add_argument(
        "-p", "--profile", type=str, help="Profile of the entry.", default="default"
    )
    return profile_parser
