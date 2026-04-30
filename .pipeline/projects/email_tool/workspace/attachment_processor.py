"""Attachment processor for handling email attachments."""

import os
import shutil
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from email_tool.attachment_types import (
    AttachmentType,
    get_attachment_type,
    is_text_attachment,
    is_image_attachment,
    is_office_attachment,
    is_pdf_attachment,
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

logger = logging.getLogger(__name__)


class AttachmentProcessor:
    """Process email attachments using appropriate parsers."""
    
    def __init__(
        self,
        base_path: str,
        dry_run: bool = False,
        collision_strategy: str = "rename",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        save_path: Optional[str] = None,
    ):
        """
        Initialize the attachment processor.
        
        Args:
            base_path: Base path for processing
            dry_run: If True, don't actually perform file operations
            collision_strategy: How to handle file collisions (rename, overwrite, skip)
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Delay between retries in seconds
            save_path: Path to save processed files
        """
        self.base_path = base_path
        self.dry_run = dry_run
        self.collision_strategy = collision_strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.save_path = save_path or base_path
        
        # Initialize parsers
        self.parsers = {
            AttachmentType.PDF: PDFAttachmentParser(base_path),
            AttachmentType.DOCX: OfficeAttachmentParser(base_path),
            AttachmentType.XLSX: OfficeAttachmentParser(base_path),
            AttachmentType.PPTX: OfficeAttachmentParser(base_path),
            AttachmentType.TXT: TextAttachmentParser(base_path),
            AttachmentType.CSV: TextAttachmentParser(base_path),
            AttachmentType.JPG: ImageAttachmentParser(base_path),
            AttachmentType.PNG: ImageAttachmentParser(base_path),
            AttachmentType.GIF: ImageAttachmentParser(base_path),
            AttachmentType.BMP: ImageAttachmentParser(base_path),
            AttachmentType.ZIP: ZipAttachmentParser(base_path),
            AttachmentType.UNKNOWN: None,
        }
        
        # Statistics
        self.stats = {
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "by_type": {},
            "by_parser": {},
        }
    
    def get_parser(self, attachment_type: AttachmentType) -> Optional[Any]:
        """Get the appropriate parser for an attachment type."""
        return self.parsers.get(attachment_type)
    
    def process_attachment(
        self,
        file_path: str,
        attachment_id: str,
        email_id: str,
        original_filename: str,
        content_type: str,
        size_bytes: int,
        attachment_type: Optional[AttachmentType] = None,
    ) -> AttachmentProcessingResult:
        """
        Process a single attachment.
        
        Args:
            file_path: Path to the attachment file
            attachment_id: Unique ID for this attachment
            email_id: ID of the email containing this attachment
            original_filename: Original filename of the attachment
            content_type: MIME type of the attachment
            size_bytes: Size of the attachment in bytes
            attachment_type: Type of attachment (will be detected if not provided)
            
        Returns:
            AttachmentProcessingResult with processing outcome
        """
        # Detect attachment type if not provided
        if attachment_type is None:
            attachment_type = get_attachment_type(
                mime_type=content_type,
                filename=original_filename
            )
        
        # Update statistics
        self.stats["total_processed"] += 1
        if attachment_type.value not in self.stats["by_type"]:
            self.stats["by_type"][attachment_type.value] = {"processed": 0, "successful": 0, "failed": 0}
        
        # Get appropriate parser
        parser = self.get_parser(attachment_type)
        
        # Handle UNKNOWN attachment type - still process successfully without parsing
        if attachment_type == AttachmentType.UNKNOWN:
            self.stats["total_successful"] += 1
            self.stats["by_type"][attachment_type.value]["successful"] += 1
            self.stats["by_parser"]["UNKNOWN"] = self.stats["by_parser"].get("UNKNOWN", 0) + 1
            
            return AttachmentProcessingResult(
                success=True,
                attachment_id=attachment_id,
                email_id=email_id,
                attachment_type=attachment_type,
                text_content=None,
                metadata=None,
                processed_at=datetime.now().isoformat(),
            )
        
        if parser is None:
            result = AttachmentProcessingResult(
                success=False,
                attachment_id=attachment_id,
                email_id=email_id,
                attachment_type=attachment_type,
                error_message=f"No parser available for attachment type: {attachment_type.value}",
                processed_at=datetime.now().isoformat(),
            )
            self.stats["total_failed"] += 1
            self.stats["by_type"][attachment_type.value]["failed"] += 1
            return result
        
        # Parse the attachment
        try:
            parsed = parser.parse(
                file_path=file_path,
                attachment_id=attachment_id,
                email_id=email_id,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=size_bytes,
                attachment_type=attachment_type,
            )
            
            if parsed.success:
                self.stats["total_successful"] += 1
                self.stats["by_type"][attachment_type.value]["successful"] += 1
                self.stats["by_parser"][type(parser).__name__] = self.stats["by_parser"].get(type(parser).__name__, 0) + 1
                
                return AttachmentProcessingResult(
                    success=True,
                    attachment_id=attachment_id,
                    email_id=email_id,
                    attachment_type=attachment_type,
                    text_content=parsed.text_content,
                    metadata=parsed.metadata,
                    processed_at=datetime.now().isoformat(),
                )
            else:
                self.stats["total_failed"] += 1
                self.stats["by_type"][attachment_type.value]["failed"] += 1
                
                return AttachmentProcessingResult(
                    success=False,
                    attachment_id=attachment_id,
                    email_id=email_id,
                    attachment_type=attachment_type,
                    error_message=parsed.error_message,
                    processed_at=datetime.now().isoformat(),
                )
                
        except Exception as e:
            logger.error(f"Error processing attachment {attachment_id}: {str(e)}")
            self.stats["total_failed"] += 1
            self.stats["by_type"][attachment_type.value]["failed"] += 1
            
            return AttachmentProcessingResult(
                success=False,
                attachment_id=attachment_id,
                email_id=email_id,
                attachment_type=attachment_type,
                error_message=str(e),
                processed_at=datetime.now().isoformat(),
            )
    
    def process_attachments(
        self,
        email: Email,
        attachments: List[str],
        action_type: str = "process",
    ) -> List[AttachmentProcessingResult]:
        """
        Process multiple attachments for an email.
        
        Args:
            email: Email object containing the attachments
            attachments: List of file paths to process
            action_type: Type of action to perform
            
        Returns:
            List of AttachmentProcessingResult objects
        """
        results = []
        
        for file_path in attachments:
            # Skip non-existent files
            if not os.path.exists(file_path):
                logger.warning(f"Attachment file not found: {file_path}")
                continue
            
            # Get attachment info
            filename = os.path.basename(file_path)
            size_bytes = os.path.getsize(file_path)
            content_type = "application/octet-stream"  # Default
            
            # Process the attachment
            result = self.process_attachment(
                file_path=file_path,
                attachment_id=f"{email.id}_{filename}",
                email_id=email.id,
                original_filename=filename,
                content_type=content_type,
                size_bytes=size_bytes,
            )
            
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "total_processed": self.stats["total_processed"],
            "total_successful": self.stats["total_successful"],
            "total_failed": self.stats["total_failed"],
            "success_rate": (
                self.stats["total_successful"] / self.stats["total_processed"]
                if self.stats["total_processed"] > 0 else 0.0
            ),
            "by_type": self.stats["by_type"],
            "by_parser": self.stats["by_parser"],
        }
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = {
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "by_type": {},
            "by_parser": {},
        }


class AttachmentDispatcher:
    """Dispatch attachments to appropriate locations based on action."""
    
    def __init__(
        self,
        base_path: str,
        dry_run: bool = False,
        collision_strategy: str = "rename",
    ):
        """
        Initialize the attachment dispatcher.
        
        Args:
            base_path: Base path for operations
            dry_run: If True, don't actually perform file operations
            collision_strategy: How to handle file collisions
        """
        self.base_path = base_path
        self.dry_run = dry_run
        self.collision_strategy = collision_strategy
    
    def _resolve_collision(self, target_path: str) -> str:
        """
        Resolve file collision based on strategy.
        
        Args:
            target_path: Original target path
            
        Returns:
            Resolved path that doesn't conflict
        """
        if not os.path.exists(target_path):
            return target_path
        
        if self.collision_strategy == "overwrite":
            return target_path
        
        elif self.collision_strategy == "skip":
            # Return None to indicate skip
            return None
        
        elif self.collision_strategy == "rename":
            # Default: add timestamp or counter
            base, ext = os.path.splitext(target_path)
            counter = 1
            while True:
                new_path = f"{base}_{counter}{ext}"
                if not os.path.exists(new_path):
                    return new_path
                counter += 1
        
        return target_path
    
    def save_attachment(
        self,
        file_path: str,
        target_path: str,
        attachment_id: str,
    ) -> Dict[str, Any]:
        """
        Save an attachment to the target location.
        
        Args:
            file_path: Source file path
            target_path: Target file path
            attachment_id: ID of the attachment
            
        Returns:
            Operation result dictionary
        """
        if self.dry_run:
            return {
                "success": True,
                "operation": "save",
                "attachment_id": attachment_id,
                "source": file_path,
                "target": target_path,
                "final_path": target_path,
                "dry_run": True,
            }
        
        # Resolve collision
        resolved_path = self._resolve_collision(target_path)
        if resolved_path is None:
            return {
                "success": False,
                "operation": "save",
                "attachment_id": attachment_id,
                "error": "Collision and skip strategy",
            }
        
        try:
            # Ensure target directory exists
            target_dir = os.path.dirname(resolved_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, resolved_path)
            
            return {
                "success": True,
                "operation": "save",
                "attachment_id": attachment_id,
                "source": file_path,
                "target": resolved_path,
                "final_path": resolved_path,
            }
            
        except Exception as e:
            logger.error(f"Error saving attachment {attachment_id}: {str(e)}")
            return {
                "success": False,
                "operation": "save",
                "attachment_id": attachment_id,
                "error": str(e),
            }
    
    def move_attachment(
        self,
        file_path: str,
        target_path: str,
        attachment_id: str,
    ) -> Dict[str, Any]:
        """
        Move an attachment to the target location.
        
        Args:
            file_path: Source file path
            target_path: Target file path
            attachment_id: ID of the attachment
            
        Returns:
            Operation result dictionary
        """
        if self.dry_run:
            return {
                "success": True,
                "operation": "move",
                "attachment_id": attachment_id,
                "source": file_path,
                "target": target_path,
                "dry_run": True,
            }
        
        # Resolve collision
        resolved_path = self._resolve_collision(target_path)
        if resolved_path is None:
            return {
                "success": False,
                "operation": "move",
                "attachment_id": attachment_id,
                "error": "Collision and skip strategy",
            }
        
        try:
            # Ensure target directory exists
            target_dir = os.path.dirname(resolved_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            # Move file
            shutil.move(file_path, resolved_path)
            
            return {
                "success": True,
                "operation": "move",
                "attachment_id": attachment_id,
                "source": file_path,
                "target": resolved_path,
                "final_path": resolved_path,
            }
            
        except Exception as e:
            logger.error(f"Error moving attachment {attachment_id}: {str(e)}")
            return {
                "success": False,
                "operation": "move",
                "attachment_id": attachment_id,
                "error": str(e),
            }
    
    def delete_attachment(
        self,
        file_path: str,
        attachment_id: str,
    ) -> Dict[str, Any]:
        """
        Delete an attachment.
        
        Args:
            file_path: Path to file to delete
            attachment_id: ID of the attachment
            
        Returns:
            Operation result dictionary
        """
        if self.dry_run:
            return {
                "success": True,
                "operation": "delete",
                "attachment_id": attachment_id,
                "file_path": file_path,
                "dry_run": True,
            }
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return {
                "success": True,
                "operation": "delete",
                "attachment_id": attachment_id,
                "file_path": file_path,
            }
            
        except Exception as e:
            logger.error(f"Error deleting attachment {attachment_id}: {str(e)}")
            return {
                "success": False,
                "operation": "delete",
                "attachment_id": attachment_id,
                "error": str(e),
            }


class AttachmentActionExecutor:
    """Execute actions on attachments based on configuration."""
    
    def __init__(
        self,
        dispatcher: AttachmentDispatcher,
        processor: AttachmentProcessor,
        max_retries: int = 3,
    ):
        """
        Initialize the action executor.
        
        Args:
            dispatcher: Attachment dispatcher for file operations
            processor: Attachment processor for parsing
            max_retries: Maximum retry attempts for operations
        """
        self.dispatcher = dispatcher
        self.processor = processor
        self.max_retries = max_retries
    
    def execute_action(
        self,
        file_path: str,
        attachment_id: str,
        email_id: str,
        action_type: str,
        target_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an action on an attachment.
        
        Args:
            file_path: Path to the attachment
            attachment_id: ID of the attachment
            email_id: ID of the email
            action_type: Type of action (save, move, delete, process)
            target_path: Target path for save/move operations
            
        Returns:
            Execution result dictionary
        """
        if action_type == "save":
            if target_path is None:
                target_path = os.path.join(self.dispatcher.base_path, os.path.basename(file_path))
            
            return self.dispatcher.save_attachment(
                file_path=file_path,
                target_path=target_path,
                attachment_id=attachment_id,
            )
        
        elif action_type == "move":
            if target_path is None:
                return {
                    "success": False,
                    "error": "Target path required for move operation",
                }
            
            return self.dispatcher.move_attachment(
                file_path=file_path,
                target_path=target_path,
                attachment_id=attachment_id,
            )
        
        elif action_type == "delete":
            return self.dispatcher.delete_attachment(
                file_path=file_path,
                attachment_id=attachment_id,
            )
        
        elif action_type == "process":
            # Process the attachment
            filename = os.path.basename(file_path)
            size_bytes = os.path.getsize(file_path)
            
            result = self.processor.process_attachment(
                file_path=file_path,
                attachment_id=attachment_id,
                email_id=email_id,
                original_filename=filename,
                content_type="application/octet-stream",
                size_bytes=size_bytes,
            )
            
            return {
                "success": result.success,
                "operation": "process",
                "attachment_id": attachment_id,
                "result": {
                    "success": result.success,
                    "attachment_type": result.attachment_type.value,
                    "text_content": result.text_content,
                    "metadata": result.metadata,
                    "error_message": result.error_message,
                },
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}",
            }


class AttachmentPipelineExecutor:
    """Execute attachment processing pipeline."""
    
    def __init__(
        self,
        processor: AttachmentProcessor,
        dispatcher: AttachmentDispatcher,
        executor: AttachmentActionExecutor,
    ):
        """
        Initialize the pipeline executor.
        
        Args:
            processor: Attachment processor
            dispatcher: Attachment dispatcher
            executor: Action executor
        """
        self.processor = processor
        self.dispatcher = dispatcher
        self.executor = executor
    
    def execute(
        self,
        email: Email,
        attachments: List[str],
        action_type: str = "process",
    ) -> List[Dict[str, Any]]:
        """
        Execute the pipeline for an email's attachments.
        
        Args:
            email: Email object
            attachments: List of attachment file paths
            action_type: Type of action to perform
            
        Returns:
            List of execution results
        """
        results = []
        
        for file_path in attachments:
            if not os.path.exists(file_path):
                logger.warning(f"Attachment file not found: {file_path}")
                continue
            
            attachment_id = f"{email.id}_{os.path.basename(file_path)}"
            
            result = self.executor.execute_action(
                file_path=file_path,
                attachment_id=attachment_id,
                email_id=email.id,
                action_type=action_type,
            )
            
            # Add attachment_type to result for all action types
            if "result" in result:
                result["attachment_type"] = result["result"].get("attachment_type", "UNKNOWN")
            elif action_type == "process":
                # For process action, extract from processor result
                result["attachment_type"] = result.get("result", {}).get("attachment_type", "UNKNOWN")
            else:
                # For save/move/delete, detect attachment type from filename
                from email_tool.attachment_types import get_attachment_type
                result["attachment_type"] = get_attachment_type(
                    mime_type="application/octet-stream",
                    filename=os.path.basename(file_path)
                ).value
            
            results.append(result)
        
        return results


class AttachmentPipelineMonitor:
    """Monitor and report on pipeline performance."""
    
    def __init__(self, processor: AttachmentProcessor):
        """
        Initialize the pipeline monitor.
        
        Args:
            processor: Attachment processor to monitor
        """
        self.processor = processor
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall pipeline status."""
        stats = self.processor.get_stats()
        return {
            "total_processed": stats["total_processed"],
            "total_successful": stats["total_successful"],
            "total_failed": stats["total_failed"],
            "success_rate": stats["success_rate"],
        }
    
    def get_parser_performance(self) -> Dict[str, Any]:
        """Get performance by parser."""
        stats = self.processor.get_stats()
        return stats.get("by_parser", {})
    
    def get_type_performance(self) -> Dict[str, Any]:
        """Get performance by attachment type."""
        stats = self.processor.get_stats()
        return stats.get("by_type", {})


class AttachmentPipelineConfig:
    """Configuration for attachment processing pipeline."""
    
    def __init__(
        self,
        base_path: str = "",
        dry_run: bool = False,
        collision_strategy: str = "rename",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        save_path: Optional[str] = None,
    ):
        """
        Initialize pipeline configuration.
        
        Args:
            base_path: Base path for processing
            dry_run: If True, don't perform actual operations
            collision_strategy: How to handle file collisions
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
            save_path: Path to save processed files
        """
        self.base_path = base_path
        self.dry_run = dry_run
        self.collision_strategy = collision_strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.save_path = save_path
    
    def to_executor(self) -> AttachmentPipelineExecutor:
        """Convert config to pipeline executor."""
        processor = AttachmentProcessor(
            base_path=self.base_path,
            dry_run=self.dry_run,
            collision_strategy=self.collision_strategy,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            save_path=self.save_path,
        )
        
        dispatcher = AttachmentDispatcher(
            base_path=self.base_path,
            dry_run=self.dry_run,
            collision_strategy=self.collision_strategy,
        )
        
        executor = AttachmentActionExecutor(
            dispatcher=dispatcher,
            processor=processor,
            max_retries=self.max_retries,
        )
        
        return AttachmentPipelineExecutor(
            processor=processor,
            dispatcher=dispatcher,
            executor=executor,
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AttachmentPipelineConfig':
        """Create config from dictionary."""
        return cls(
            base_path=config_dict.get("base_path", ""),
            dry_run=config_dict.get("dry_run", False),
            collision_strategy=config_dict.get("collision_strategy", "rename"),
            max_retries=config_dict.get("max_retries", 3),
            retry_delay=config_dict.get("retry_delay", 1.0),
            save_path=config_dict.get("save_path"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "base_path": self.base_path,
            "dry_run": self.dry_run,
            "collision_strategy": self.collision_strategy,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "save_path": self.save_path,
        }


class AttachmentPipelineBuilder:
    """Builder for creating attachment pipeline configurations."""
    
    def __init__(self):
        """Initialize the builder."""
        self.config = AttachmentPipelineConfig()
    
    def set_base_path(self, path: str) -> 'AttachmentPipelineBuilder':
        """Set the base path for processing."""
        self.config.base_path = path
        return self
    
    def set_dry_run(self, dry_run: bool) -> 'AttachmentPipelineBuilder':
        """Set dry run mode."""
        self.config.dry_run = dry_run
        return self
    
    def set_collision_strategy(self, strategy: str) -> 'AttachmentPipelineBuilder':
        """Set collision handling strategy."""
        self.config.collision_strategy = strategy
        return self
    
    def set_max_retries(self, max_retries: int) -> 'AttachmentPipelineBuilder':
        """Set maximum retry attempts."""
        self.config.max_retries = max_retries
        return self
    
    def set_retry_delay(self, retry_delay: float) -> 'AttachmentPipelineBuilder':
        """Set delay between retries."""
        self.config.retry_delay = retry_delay
        return self
    
    def set_save_path(self, save_path: str) -> 'AttachmentPipelineBuilder':
        """Set save path for processed files."""
        self.config.save_path = save_path
        return self
    
    def set_retry_config(self, max_retries: int, retry_delay: float) -> 'AttachmentPipelineBuilder':
        """Set retry configuration."""
        self.config.max_retries = max_retries
        self.config.retry_delay = retry_delay
        return self
    
    def build(self) -> AttachmentPipelineExecutor:
        """Build and return a pipeline executor."""
        return self.config.to_executor()
    
    def build_config(self) -> AttachmentPipelineConfig:
        """Build and return a configuration."""
        return self.config
