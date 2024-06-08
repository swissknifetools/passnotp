from enum import Enum


class LogLevel(str, Enum):
    """Log level constants."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogLevelColor(str, Enum):
    """Log level color constants."""

    DEBUG = "\033[1;35m"
    INFO = "\033[1;34m"
    WARNING = "\033[1;33m"
    ERROR = "\033[1;31m"
    CRITICAL = "\033[1;41m"

    NO_COLOR = "\033[0m"
    WHITE = "\033[1;37m"
