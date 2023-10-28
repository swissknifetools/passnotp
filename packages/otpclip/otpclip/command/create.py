import base64
import pyotp
from otpclip.config.logging import logger

def create_otp(identifier: str, key: str) -> None:
    totp = pyotp.TOTP(key)
    logger.info(totp.now())
    