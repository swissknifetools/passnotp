import logging

from libs.shared.logging import ClickEchoHandler, LogLevel

# HANDLER
log_handler = ClickEchoHandler()
log_handler.setLevel(getattr(logging, LogLevel.DEBUG))

# LOGGER
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LogLevel.DEBUG))
logger.addHandler(log_handler)
