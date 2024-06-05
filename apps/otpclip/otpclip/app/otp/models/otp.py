from otpclip.app.core.db.engine import Base

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class OTP(Base):
    __tablename__ = "otp"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    myname: Mapped[str] = mapped_column(String(30), nullable=False)
