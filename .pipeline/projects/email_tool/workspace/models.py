"""Data models for email processing."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class AttachmentType(Enum):
    """Supported attachment types."""
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    TXT = "TXT"
    CSV = "CSV"
    JPG = "JPG"
    PNG = "PNG"
    UNKNOWN = "UNKNOWN"


@dataclass
class Email:
    """Email data model."""
    id: str
    subject: str
    sender: str
    recipients: List[str]
    body: str
    raw_headers: Dict[str, str]
    attachments: List[str] = field(default_factory=list)
    processed_at: Optional[datetime] = None
    status: str = "pending"
    error_message: Optional[str] = None


@dataclass
class AttachmentProcessingResult:
    """Result of processing an attachment."""
    success: bool
    attachment_id: str
    email_id: str
    attachment_type: str
    text_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processed_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmailAttachmentProcessingResult:
    """Result of processing all attachments for an email."""
    email_id: str
    total_attachments: int
    successful: int
    failed: int
    results: List[AttachmentProcessingResult] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.now)
