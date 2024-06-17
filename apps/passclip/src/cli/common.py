import argparse

from libs.config.src.cli.config.dto import ConfigSettings
from libs.console_logger.src.constants import LogLevel


def get_common_parser() -> argparse.ArgumentParser:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_options = common_parser.add_argument_group(title="global")
    common_options.add_argument(
        "-l",
        "--log_level",
        choices=[x.value for x in LogLevel],
        default="INFO",
        action="store",
        help="sets log level",
    )
    common_options.add_argument(
        "-nc",
        "--no_color",
        action="store_true",
        default=False,
        help="disables color output",
    )

    return common_parser
