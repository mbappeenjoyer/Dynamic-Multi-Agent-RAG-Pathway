from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from db import Base  

class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    tools = relationship("ChatTool", back_populates="chat", cascade="all, delete-orphan")
    files = relationship("ChatFile", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    feedback = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="messages")

class ChatTool(Base):
    __tablename__ = "chat_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))
    name = Column(String)
    description = Column(String)
    python_code = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="tools")

class ChatFile(Base):
    __tablename__ = "chat_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"))
    filename = Column(String)
    original_filename = Column(String)
    file_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="files") 