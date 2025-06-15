from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.base import Base


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    # relationship
    messages = relationship('Message', uselist=True, viewonly=True,
                            primaryjoin='Chat.id == Message.chat_id', )

    def __repr__(self):
        return f'< Id: {self.id}, Telegram Id: {self.telegram_id} >'


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey('chats.id'), nullable=True)
    content = Column(Text())
    role = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f'< Id: {self.id}, Content: {self.content} >'
