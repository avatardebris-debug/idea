"""Base classes for attachment processing."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class AttachmentMetadata:
    """Metadata for a parsed attachment."""
    
    file_size: int = 0
    file_type: str = ""
    parsed_at: datetime = field(default_factory=datetime.now)
    parser_name: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key):
        """Allow subscript access for compatibility."""
        return getattr(self, key, None)


@dataclass
class ParsedAttachment:
    """Result of parsing an attachment."""
    
    success: bool = False
    text_content: str = ""
    metadata: Optional[AttachmentMetadata] = None
    error_message: Optional[str] = None
    attachment_id: str = ""
    email_id: str = ""
    original_filename: str = ""
    content_type: str = ""
    size_bytes: int = 0
    attachment_type: str = ""
