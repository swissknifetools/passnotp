import logging

from libs.console_logger.src.constants import LogLevel, LogLevelColor
from libs.console_logger.src.formatter import ColoredFormatter
from libs.console_logger.src.handler import ConsoleHandler


def get_console_handler(
    log_level: LogLevel = LogLevel.INFO, use_color: bool = True
) -> ConsoleHandler:
    """Function to easily create a console handler.

    Args:
        log_level (:enum:`LogLevel`, optional): Log level to set the handler to. Defaults to LogLevel.INFO.
        use_color (bool, optional): Flag to enable or disable color output. Defaults to True.

    Returns:
        ConsoleHandler: Handler object.
    """
    ch = ConsoleHandler()

    ch.setLevel(getattr(logging, log_level))
    ch.setFormatter(ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=use_color))
    return ch
