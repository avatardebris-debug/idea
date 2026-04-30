"""ZIP attachment parser."""

import os
import zipfile
import tempfile
import shutil
from typing import Optional, List

from email_tool.attachment_parsers.base import ParsedAttachment, AttachmentMetadata


class ZipAttachmentParser:
    """Parser for ZIP attachments."""
    
    def __init__(self, base_path: str):
        """Initialize the ZIP parser."""
        self.base_path = base_path
        self.parser_name = "ZipAttachmentParser"
    
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
        """Parse a ZIP file and list its contents."""
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
            
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    text_content = "ZIP contents:\n" + "\n".join(file_list)
            except zipfile.BadZipFile:
                text_content = "[Not a valid ZIP file]"
            
            metadata = AttachmentMetadata(
                file_size=size_bytes,
                file_type=content_type,
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
