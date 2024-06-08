import argparse

from rich_argparse import RichHelpFormatter

from apps.passclip.src.cli.config.cli import add_config_cli
from apps.passclip.src.cli.passclip.cli import add_passclip_cli
from libs.console_logger.src.constants import LogLevel


def get_main_parser(
    common_parser: argparse.ArgumentParser,
    no_color: bool = False,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="passclip",
        description="passclip is a command-line tool for managing passwords.",
        epilog="Author: Joni Seraj, Ergi Kame",
        allow_abbrev=True,
        parents=[common_parser],
        formatter_class=argparse.HelpFormatter if no_color else RichHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1.0")

    command_sp = parser.add_subparsers(title="commands", dest="command")

    add_passclip_cli(command_sp, common_parser, no_color)
    add_config_cli(command_sp, common_parser, no_color)

    return parser
