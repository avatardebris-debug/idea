"""PDF attachment parser."""

import os
from typing import Optional

from email_tool.attachment_parsers.base import ParsedAttachment, AttachmentMetadata


class PDFAttachmentParser:
    """Parser for PDF attachments."""
    
    def __init__(self, base_path: str):
        """Initialize the PDF parser."""
        self.base_path = base_path
        self.parser_name = "PDFAttachmentParser"
    
    def parse(
        self,
        file_path: str,
        attachment_id: str,
        email_id: str,
        original_filename: str,
        content_type: str,
        size_bytes: int,
        attachment_type: str
    ) -> ParsedAttachment:
        """Parse a PDF file and extract text content."""
        try:
            if not os.path.exists(file_path):
                return ParsedAttachment(
                    success=False,
                    error_message=f"File not found: {file_path}",
                    attachment_id=attachment_id,
                    email_id=email_id,
                    original_filename=original_filename,
                    content_type=content_type,
                    size_bytes=size_bytes,
                    attachment_type=attachment_type
                )
            
            # Try pypdf first
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text_content = "\n".join(text_parts)
            except ImportError:
                # Fallback to pdfplumber
                try:
                    import pdfplumber
                    text_parts = []
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                    text_content = "\n".join(text_parts)
                except ImportError:
                    # If neither library is available, return metadata only
                    text_content = "[PDF text extraction requires pypdf or pdfplumber]"
            
            metadata = AttachmentMetadata(
                file_size=size_bytes,
                file_type="application/pdf",
                parser_name=self.parser_name
            )
            
            return ParsedAttachment(
                success=True,
                text_content=text_content,
                metadata=metadata,
                attachment_id=attachment_id,
                email_id=email_id,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=size_bytes,
                attachment_type=attachment_type
            )
            
        except Exception as e:
            return ParsedAttachment(
                success=False,
                error_message=str(e),
                attachment_id=attachment_id,
                email_id=email_id,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=size_bytes,
                attachment_type=attachment_type
            )
