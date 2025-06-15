from typing import Optional, List
from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base
from database.models.gpt import Message


class User(Base):
    __tablename__ = 'users'
    telegram_id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True)
    username: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    wallet_address: Mapped[Optional[str]]
    keystore = mapped_column(sa.JSON(), default={})

    messages: Mapped[List[Message]] = relationship(
        'Message', uselist=True, viewonly=True, primaryjoin='User.telegram_id == Message.telegram_id'
    )

    def __repr__(self):
        return f'< Username: {self.username}, Telegram Id: {self.telegram_id} >'


class Contact(Base):
    __tablename__ = 'contacts'
    telegram_id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True)
    contact_name: Mapped[str]
    wallet_address: Mapped[str]
