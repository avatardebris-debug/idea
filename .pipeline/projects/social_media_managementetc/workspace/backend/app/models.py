from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")
    tables = relationship("ContentTable", back_populates="workspace", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    platform = Column(String, nullable=False)  # twitter, instagram, etc.
    account_name = Column(String, nullable=True)
    account_id = Column(String, nullable=True)  # platform-specific ID
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace")


class ContentTable(Base):
    __tablename__ = "content_tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    column_definitions = Column(JSON, nullable=False)  # list of column specs
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace")
    records = relationship("ContentRecord", back_populates="table", cascade="all, delete-orphan")


class ContentRecord(Base):
    __tablename__ = "content_records"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("content_tables.id"), nullable=False)
    data = Column(JSON, nullable=False)  # column_name -> value mapping
    status = Column(String, default="draft")
    scheduled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    table = relationship("ContentTable", back_populates="records")
