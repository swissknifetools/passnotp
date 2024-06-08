import argparse

from rich_argparse import RichHelpFormatter


def add_config_cli(
    command_sp: argparse._SubParsersAction,
    common_parser: argparse.ArgumentParser,
    no_color: bool = False,
) -> None:
    config_parser = command_sp.add_parser(
        "config",
        help="Configuration commands",
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    config_subparsers = config_parser.add_subparsers(title="config", dest="subcommand")

    # COMMANDS
    config_subparsers.add_parser(
        "init",
        help="Initialize a new config file.",
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )

    config_subparsers.add_parser(
        "show",
        help="Show the config file.",
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
