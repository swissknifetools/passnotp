from multiprocessing import process
import os
import signal
import subprocess
import pyotp
from otpclip.app.core.logging.logging import logger
import pyperclip


def create_otp(identifier: str, key: str) -> None:
    logger.info(identifier)
    logger.info(key)
    totp = pyotp.TOTP(key.replace(" ", ""))
    logger.info(totp.now())
    logger.info(os.getpid())
    logger.info(os.getppid())
    logger.info(os.getpgrp())
    logger.info(os.getpgid(os.getppid()))
    pyperclip.copy(totp.now())
    os.kill(os.getppid(), signal.SIGHUP)
