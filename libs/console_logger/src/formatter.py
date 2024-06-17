import logging
import re

from libs.console_logger.src.constants import LogLevelColor


class ColoredFormatter(logging.Formatter):
    """Color logging formatter.

    Args:
        fmt (str): Format string, typically one of the standard logging module formats.
        use_color (bool, optional): Flag to enable or disable color output. Defaults to True.
    """

    def __init__(self, fmt: str, use_color: bool = True):
        super().__init__(fmt)
        self.use_color = use_color
        self.ANSI_ESCAPE = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")

    def format(self, record):
        super().format(record)
        if not self.use_color:
            return self.ANSI_ESCAPE.sub(
                "", f"[{record.levelname}] %(asctime)s - %(message)s" % record.__dict__
            )
        return (
            f"{LogLevelColor[record.levelname].value}[{record.levelname}]{LogLevelColor.NO_COLOR.value} {LogLevelColor.WHITE.value}%(asctime)s{LogLevelColor.NO_COLOR.value} - %(message)s"
            % record.__dict__
        )
