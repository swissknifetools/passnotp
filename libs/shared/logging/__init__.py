import logging
from enum import Enum

import click


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ClickEchoHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        if record.levelno == logging.DEBUG:
            click.echo(f"{click.style('[DEBUG]', fg='bright_black')} {log_entry}", color=True)
        elif record.levelno == logging.INFO: 
            click.echo(f"{click.style('[INFO]', fg='blue')} {log_entry}", color=True)
        elif record.levelno == logging.WARNING: 
            click.echo(f"{click.style('[WARNING]', fg='yellow')} {log_entry}", color=True)
        elif record.levelno == logging.ERROR: 
            click.echo(f"{click.style('[ERROR]', fg='red')} {log_entry}", color=True)
        else:
            click.echo(f"{log_entry}")