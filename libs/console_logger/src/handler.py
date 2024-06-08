import logging


class ConsoleHandler(logging.Handler):
    """Console logging handler."""

    def emit(self, record):
        log_entry = self.format(record)
        print(f"{log_entry}")
