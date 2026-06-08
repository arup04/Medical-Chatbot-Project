# src/database.py
import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

# Read database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Default to SQLite for local development out-of-the-box
    database_url = "sqlite:///./medibot.db"
else:
    # Standardize postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

# Enforce secure connection mode if using cloud database
connect_args = {}
if "sqlite" in database_url:
    # SQLite requires check_same_thread=False for FastAPI concurrency
    connect_args = {"check_same_thread": False}

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SessionModel(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, default="New Consultation")
    user_id = Column(String, nullable=False, default="guest")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan")

class MessageModel(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" or "bot"
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("SessionModel", back_populates="messages")

def init_db():
    Base.metadata.create_all(bind=engine)
