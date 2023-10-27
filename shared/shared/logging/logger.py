import logging
from enum import Enum

import click

from shared.env import environment


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
                
        
        

# HANDLER
log_handler = ClickEchoHandler()
log_handler.setLevel(getattr(logging, environment.LOGGING_LEVEL))

# LOGGER
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, environment.LOGGING_LEVEL))
logger.addHandler(log_handler)