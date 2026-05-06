"""
Database models for HR Telegram WebApp Bot
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, func
from db import Base


class User(Base):
    """
    Telegram user model
    Stores user information from Telegram
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="en")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username='{self.username}')>"


class ChatLog(Base):
    """
    MODULE 2: Chat logs table
    Stores all conversations between users and the bot
    
    Schema:
    - id (primary key)
    - user_id (string)
    - language (string)
    - message (text)
    - response (text)
    - created_at (timestamp, default now())
    """
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    language = Column(String(10), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ChatLog(id={self.id}, user_id='{self.user_id}', lang='{self.language}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "language": self.language,
            "message": self.message,
            "response": self.response,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
