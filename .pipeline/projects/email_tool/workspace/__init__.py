"""Email Tool - Email attachment processing and management."""

from email_tool.attachment_types import (
    AttachmentType,
    get_attachment_type,
    is_text_attachment,
    is_image_attachment,
    is_office_attachment,
    is_pdf_attachment,
    get_supported_types,
)

from email_tool.attachment_parsers.base import (
    AttachmentMetadata,
    ParsedAttachment,
)

from email_tool.attachment_parsers.pdf import PDFAttachmentParser
from email_tool.attachment_parsers.office import OfficeAttachmentParser
from email_tool.attachment_parsers.text import TextAttachmentParser
from email_tool.attachment_parsers.image import ImageAttachmentParser
from email_tool.attachment_parsers.zip import ZipAttachmentParser

from email_tool.models import (
    Email,
    AttachmentProcessingResult,
    EmailAttachmentProcessingResult,
)

from email_tool.attachment_processor import (
    AttachmentPipelineConfig,
    AttachmentProcessor,
    AttachmentDispatcher,
    AttachmentActionExecutor,
    AttachmentPipelineExecutor,
    AttachmentPipelineMonitor,
    AttachmentPipelineBuilder,
)

__version__ = "1.0.0"
__all__ = [
    # Attachment types
    'AttachmentType',
    'get_attachment_type',
    'is_text_attachment',
    'is_image_attachment',
    'is_office_attachment',
    'is_pdf_attachment',
    'get_supported_types',
    # Parsers
    'AttachmentMetadata',
    'ParsedAttachment',
    'PDFAttachmentParser',
    'OfficeAttachmentParser',
    'TextAttachmentParser',
    'ImageAttachmentParser',
    'ZipAttachmentParser',
    # Models
    'Email',
    'AttachmentProcessingResult',
    'EmailAttachmentProcessingResult',
    # Pipeline
    'AttachmentPipelineConfig',
    'AttachmentProcessor',
    'AttachmentDispatcher',
    'AttachmentActionExecutor',
    'AttachmentPipelineExecutor',
    'AttachmentPipelineMonitor',
    'AttachmentPipelineBuilder',
]
