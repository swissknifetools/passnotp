import logging

from otpclip.app.core.config.env import environment
from shared.logging import ClickEchoHandler

# HANDLER
log_handler = ClickEchoHandler()
log_handler.setLevel(getattr(logging, environment.LOGGING_LEVEL))

# LOGGER
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, environment.LOGGING_LEVEL))
logger.addHandler(log_handler)