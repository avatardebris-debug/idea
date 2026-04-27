from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime


# Workspace schemas
class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Account schemas
class AccountCreate(BaseModel):
    platform: str
    account_name: Optional[str] = None
    account_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class AccountResponse(BaseModel):
    id: int
    workspace_id: int
    platform: str
    account_name: Optional[str]
    account_id: Optional[str]
    is_connected: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Table schemas
class ColumnDefinition(BaseModel):
    name: str
    type: str  # text, tags, status, date, media_url
    required: bool = False
    default: Optional[Any] = None


class TableCreate(BaseModel):
    name: str
    workspace_id: int
    column_definitions: List[ColumnDefinition]

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Table name cannot be empty')
        return v


class TableUpdate(BaseModel):
    name: Optional[str] = None
    column_definitions: Optional[List[ColumnDefinition]] = None


class TableResponse(BaseModel):
    id: int
    name: str
    workspace_id: int
    column_definitions: List[ColumnDefinition]
    created_at: datetime

    class Config:
        from_attributes = True


# Record schemas
class RecordCreate(BaseModel):
    table_id: int
    data: dict[str, Any]
    status: Optional[str] = "draft"
    scheduled_date: Optional[datetime] = None


class RecordUpdate(BaseModel):
    data: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class RecordResponse(BaseModel):
    id: int
    table_id: int
    data: dict[str, Any]
    status: str
    scheduled_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Pagination schema
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int
