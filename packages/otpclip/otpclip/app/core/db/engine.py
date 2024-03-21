import os

from otpclip.app.core.config.env import environment
from shared.logging import LogLevel
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

dir = os.path.dirname('~/.otpclip/')
loc = os.path.join(dir, 'otp.db')

engine = create_engine(f'sqlite:///{os.path.expanduser(loc)}', echo=True if environment.LOGGING_LEVEL == LogLevel.DEBUG else False )
engine.connect()

class Base(DeclarativeBase):
    pass

from otpclip.app.otp.models.otp import OTP

Base.metadata.create_all(engine)

