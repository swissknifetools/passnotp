import logging

from libs.console_logger.src import get_console_handler
from libs.console_logger.src.constants import LogLevel


def setup_logger(log_level: LogLevel = LogLevel.INFO, no_color: bool = False) -> logging.Logger:
    logger = logging.getLogger("passclip")
    logger.setLevel(logging.DEBUG)

    ch = get_console_handler(log_level=log_level, use_color=not no_color)
    logger.addHandler(ch)
