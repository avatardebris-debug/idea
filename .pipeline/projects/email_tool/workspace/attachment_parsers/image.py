"""Image attachment parser with OCR support."""

import os
from typing import Optional

from email_tool.attachment_parsers.base import ParsedAttachment, AttachmentMetadata


class ImageAttachmentParser:
    """Parser for image attachments with OCR support."""
    
    def __init__(self, base_path: str):
        """Initialize the image parser."""
        self.base_path = base_path
        self.parser_name = "ImageAttachmentParser"
        self.ocr_available = False
        self._check_ocr()
    
    def _check_ocr(self):
        """Check if OCR libraries are available."""
        try:
            import pytesseract
            self.ocr_available = True
        except ImportError:
            try:
                import easyocr
                self.ocr_available = True
            except ImportError:
                self.ocr_available = False
    
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
        """Parse an image file and extract text via OCR."""
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
            
            if self.ocr_available:
                try:
                    import pytesseract
                    from PIL import Image
                    img = Image.open(file_path)
                    text_content = pytesseract.image_to_string(img)
                except Exception as e:
                    text_content = f"[OCR error: {str(e)}]"
            else:
                text_content = "[OCR not available - install pytesseract or easyocr]"
            
            metadata = AttachmentMetadata(
                file_size=size_bytes,
                file_type=content_type,
                parser_name=self.parser_name,
                extra_data={"ocr_available": self.ocr_available}
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
