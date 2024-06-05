import logging

from libs.console_logger.src.constants import LogLevel, LogLevelColor


class ColoredFormatter(logging.Formatter):
    """Color logging formatter.

    Args:
        fmt (str): Format string, typically one of the standard logging module formats.
        use_color (bool, optional): Flag to enable or disable color output. Defaults to True.
    """

    def __init__(self, fmt: str, use_color: bool = True):

        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record):
        super().format(record)
        if not self.use_color:
            return f"{record.levelname} %(asctime)s - %(message)s" % record.__dict__
        return (
            f"{LogLevelColor[record.levelname].value}[{record.levelname}]{LogLevelColor.RESET.value} {LogLevelColor.WHITE.value}%(asctime)s{LogLevelColor.RESET.value} - %(message)s"
            % record.__dict__
        )


class ConsoleHandler(logging.Handler):
    """Console logging handler."""

    def emit(self, record):
        log_entry = self.format(record)
        print(f"{log_entry}")


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
