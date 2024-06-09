import argparse

from rich_argparse import RichHelpFormatter

from apps.passclip.src.cli.config.controller import config_init, config_show


def add_config_cli(
    command_sp: argparse._SubParsersAction,
    common_parser: argparse.ArgumentParser,
    no_color: bool = False,
) -> None:
    config_parser: argparse.ArgumentParser = command_sp.add_parser(
        "config",
        help="Configuration commands",
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    config_parser.set_defaults(func=config_parser.print_help)
    config_subparsers = config_parser.add_subparsers(title="config", dest="subcommand")

    # COMMANDS
    init_config_parser = config_subparsers.add_parser(
        "init",
        help="Initialize a new config file.",
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    init_config_parser.set_defaults(func=config_init)

    show_config_parser = config_subparsers.add_parser(
        "show",
        help="Show the config file.",
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    show_config_parser.set_defaults(func=config_show)
