"""Attachment type detection and classification."""

from enum import Enum
from typing import List, Optional


class AttachmentType(Enum):
    """Enumeration of supported attachment types."""
    
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    TXT = "TXT"
    CSV = "CSV"
    JPG = "JPG"
    PNG = "PNG"
    GIF = "GIF"
    BMP = "BMP"
    ZIP = "ZIP"
    UNKNOWN = "UNKNOWN"


# MIME type to attachment type mapping
MIME_TO_ATTACHMENT = {
    "application/pdf": AttachmentType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": AttachmentType.DOCX,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": AttachmentType.XLSX,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": AttachmentType.PPTX,
    "text/plain": AttachmentType.TXT,
    "text/csv": AttachmentType.CSV,
    "image/jpeg": AttachmentType.JPG,
    "image/png": AttachmentType.PNG,
    "image/gif": AttachmentType.GIF,
    "image/bmp": AttachmentType.BMP,
    "application/zip": AttachmentType.ZIP,
    "application/x-zip-compressed": AttachmentType.ZIP,
}

# File extension to attachment type mapping
EXTENSION_TO_ATTACHMENT = {
    ".pdf": AttachmentType.PDF,
    ".docx": AttachmentType.DOCX,
    ".xlsx": AttachmentType.XLSX,
    ".pptx": AttachmentType.PPTX,
    ".txt": AttachmentType.TXT,
    ".csv": AttachmentType.CSV,
    ".jpg": AttachmentType.JPG,
    ".jpeg": AttachmentType.JPG,
    ".png": AttachmentType.PNG,
    ".gif": AttachmentType.GIF,
    ".bmp": AttachmentType.BMP,
    ".zip": AttachmentType.ZIP,
}


def get_attachment_type(
    mime_type: str = "",
    filename: str = ""
) -> AttachmentType:
    """
    Determine the attachment type from MIME type or filename.
    
    Args:
        mime_type: The MIME type of the attachment
        filename: The filename of the attachment
        
    Returns:
        The detected AttachmentType
    """
    # Try MIME type first
    if mime_type:
        mime_lower = mime_type.lower().strip()
        if mime_lower in MIME_TO_ATTACHMENT:
            return MIME_TO_ATTACHMENT[mime_lower]
    
    # Try filename extension
    if filename:
        filename_lower = filename.lower()
        for ext, attachment_type in EXTENSION_TO_ATTACHMENT.items():
            if filename_lower.endswith(ext):
                return attachment_type
    
    return AttachmentType.UNKNOWN


def is_text_attachment(attachment_type: AttachmentType) -> bool:
    """Check if an attachment type is text-based."""
    return attachment_type in [
        AttachmentType.TXT,
        AttachmentType.CSV,
    ]


def is_image_attachment(attachment_type: AttachmentType) -> bool:
    """Check if an attachment type is an image."""
    return attachment_type in [
        AttachmentType.JPG,
        AttachmentType.PNG,
        AttachmentType.GIF,
        AttachmentType.BMP,
    ]


def is_office_attachment(attachment_type: AttachmentType) -> bool:
    """Check if an attachment type is an Office document."""
    return attachment_type in [
        AttachmentType.DOCX,
        AttachmentType.XLSX,
        AttachmentType.PPTX,
    ]


def is_pdf_attachment(attachment_type: AttachmentType) -> bool:
    """Check if an attachment type is a PDF."""
    return attachment_type == AttachmentType.PDF


def get_supported_types() -> List[AttachmentType]:
    """Get list of supported attachment types."""
    return [
        AttachmentType.PDF,
        AttachmentType.DOCX,
        AttachmentType.XLSX,
        AttachmentType.PPTX,
        AttachmentType.TXT,
        AttachmentType.CSV,
        AttachmentType.JPG,
        AttachmentType.PNG,
        AttachmentType.GIF,
        AttachmentType.BMP,
        AttachmentType.ZIP,
    ]
