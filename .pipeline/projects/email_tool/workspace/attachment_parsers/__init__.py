"""Attachment parsers package."""

from email_tool.attachment_parsers.base import AttachmentMetadata, ParsedAttachment
from email_tool.attachment_parsers.pdf import PDFAttachmentParser
from email_tool.attachment_parsers.office import OfficeAttachmentParser
from email_tool.attachment_parsers.text import TextAttachmentParser
from email_tool.attachment_parsers.image import ImageAttachmentParser
from email_tool.attachment_parsers.zip import ZipAttachmentParser

__all__ = [
    'AttachmentMetadata',
    'ParsedAttachment',
    'PDFAttachmentParser',
    'OfficeAttachmentParser',
    'TextAttachmentParser',
    'ImageAttachmentParser',
    'ZipAttachmentParser',
]
