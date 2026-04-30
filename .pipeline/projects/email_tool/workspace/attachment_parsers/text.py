"""Text and CSV attachment parser."""

import os
import csv
from typing import Optional

from email_tool.attachment_parsers.base import ParsedAttachment, AttachmentMetadata


class TextAttachmentParser:
    """Parser for text and CSV attachments."""
    
    def __init__(self, base_path: str):
        """Initialize the text parser."""
        self.base_path = base_path
        self.parser_name = "TextAttachmentParser"
    
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
        """Parse a text or CSV file and extract content."""
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
            
            text_content = ""
            
            if original_filename.lower().endswith('.csv'):
                # Parse CSV file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if rows:
                            text_content = "\n".join([",".join(row) for row in rows])
                        else:
                            text_content = "[Empty CSV file]"
                except Exception as e:
                    text_content = f"[CSV parsing error: {str(e)}]"
            else:
                # Parse as plain text
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        text_content = f.read()
                except Exception as e:
                    text_content = f"[Text reading error: {str(e)}]"
            
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
