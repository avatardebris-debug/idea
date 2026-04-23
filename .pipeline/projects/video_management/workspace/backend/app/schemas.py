"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, validator

from .models import FieldTypeId, VideoStatus


# ── Field schemas ──────────────────────────────────────────────

class FieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    field_type: FieldTypeId
    options: Optional[List[str]] = None
    is_required: bool = False

    @validator("options")
    def validate_options(cls, v, values):
        if values.get("field_type") == FieldTypeId.SELECT and not v:
            raise ValueError("SELECT fields must have options")
        if values.get("field_type") != FieldTypeId.SELECT and v:
            raise ValueError("Only SELECT fields can have options")
        return v


class FieldResponse(BaseModel):
    id: str
    name: str
    field_type: FieldTypeId
    options: Optional[List[str]]
    is_required: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Video schemas ──────────────────────────────────────────────

class VideoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    status: VideoStatus = VideoStatus.DRAFT
    tags: List[str] = []
    publish_date: Optional[datetime] = None
    thumbnail_url: str = ""
    youtube_video_id: Optional[str] = None
    custom_fields: dict[str, Any] = {}

    @validator("tags")
    def validate_tags(cls, v):
        return [t.strip() for t in v if t.strip()]


class VideoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[VideoStatus] = None
    tags: Optional[List[str]] = None
    publish_date: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    youtube_video_id: Optional[str] = None
    custom_fields: Optional[dict[str, Any]] = None


class VideoResponse(BaseModel):
    id: str
    title: str
    description: str
    status: VideoStatus
    tags: List[str]
    publish_date: Optional[datetime]
    thumbnail_url: str
    youtube_video_id: Optional[str]
    custom_fields: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[VideoResponse]


# ── Table schemas ──────────────────────────────────────────────

class TableMetadataCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""


class TableMetadataResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
